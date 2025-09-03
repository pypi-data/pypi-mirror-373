"""Code generation to build automation manager jobs for the platform and click commands for the RegScale CLI"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from regscale.models.integration_models.synqly_models.synqly_model import SynqlyModel

from regscale.models.integration_models.synqly_models.connector_types import ConnectorType
from regscale.models.integration_models.synqly_models.param import Param

SUPPORTED_CONNECTORS = [ConnectorType.Ticketing, ConnectorType.Vulnerabilities, ConnectorType.Assets, ConnectorType.Edr]


def generate_dags() -> None:
    """Generate Airflow DAGs for the platform"""
    from regscale.core.app.utils.app_utils import check_file_path
    from regscale.models.integration_models.synqly_models.synqly_model import SynqlyModel

    model = SynqlyModel()
    configs = model._get_integrations_and_secrets(True)
    # iterate through connectors and generate DAGs
    for connector in SUPPORTED_CONNECTORS:
        connector_configs = {
            integration: configs[integration] for integration in configs if connector in integration.lower()
        }
        # sort the connector configs by the key for repeatability
        connector_configs = dict(sorted(connector_configs.items()))
        description = _build_description(configs=connector_configs, connector=connector)
        # check airflow/dags for existing DAGs and skip them
        for integration, config in connector_configs.items():
            save_dir = f"airflow/dags/{integration.split('_')[0].lower()}"
            integration_name = integration[integration.find("_") + 1 :]
            # check if the directory exists, if not create it
            check_file_path(save_dir)
            _create_and_save_dag(
                model=model,
                integration=integration,
                config=config,
                integration_name=integration_name,
                description=description,
                save_dir=save_dir,
            )


def _create_and_save_dag(
    model: "SynqlyModel", integration: str, config: dict, integration_name: str, description: str, save_dir: str
) -> None:
    """
    Create and save a DAG for the given integration

    :param SynqlyModel model: The model to use for the DAG
    :param str integration: The integration to create the DAG for
    :param dict config: The config for the integration
    :param str integration_name: The name of the integration
    :param str description: The description for the DAG
    :param str save_dir: The directory to save the DAG to
    :rtype: None
    """
    import re

    capabilities = config.get("capabilities", [])
    op_kwargs = ""
    doc_string = f"{description}\nimage: {integration.split('_')[0]}.jpg\ndocs: None\n"
    # replace the integration config with a flattened version
    config = model._flatten_secrets(integration=integration, return_secrets=True)
    for param_type in ["expected_params", "optional_params", "required_secrets"]:
        op_kwargs, doc_string = _build_op_kwargs_and_docstring(
            config=config,
            integration=integration,
            param_type=param_type,
            op_kwargs=op_kwargs,
            doc_string=doc_string,
            capabilities=capabilities,
        )
    # add config to op_kwargs
    op_kwargs += '\n        "config": "{{ dag_run.conf }}",'
    # this indent is important to keep the code valid python
    dag_code = f"""
from airflow import DAG

from regscale.airflow.config import DEFAULT_ARGS, yesterday
from regscale.airflow.hierarchy import AIRFLOW_CLICK_OPERATORS as OPERATORS

DAG_NAME = "{integration}"

dag = DAG(
    DAG_NAME,
    default_args=DEFAULT_ARGS,
    schedule=None,
    start_date=yesterday(),
    description=__doc__,
    is_paused_upon_creation=False,
    render_template_as_native_obj=True,
)

integration_operator = OPERATORS["{integration.split('_')[0].lower()}__sync_{integration_name.lower()}"]["lambda"](
    dag=dag,
    suffix=DAG_NAME,
    op_kwargs={{{op_kwargs}\n    }},
)

integration_operator
            """
    with open(f"{save_dir}/{integration_name.lower()}.py", "w") as f:
        f.write("# flake8: noqa E501\n# pylint: disable=line-too-long\n")
        f.write('"""')
        # replace all instances of "synqly" with the integration name
        f.write(re.sub(r"(?i)synqly", integration_name, doc_string))
        f.write('"""\n')
        f.write("# pylint: enable=line-too-long\n")
        # replace all instances of "synqly" with the integration name
        f.write(re.sub(r"(?i)synqly", integration_name, dag_code))
    print(f"Generated DAG for {integration_name}.")


def _build_description(configs: dict[str, dict], connector: str) -> str:
    """
    Build the description for the DAG

    :param dict[str, dict] configs: The configs for the integrations
    :return: The description for the DAG
    :rtype: str
    """
    sync_attachments = []
    integrations = []
    for integration, config in configs.items():
        integration_name = integration.replace(f"{connector.lower()}_", "").replace("_", " ").title()
        integrations.append(integration_name)
        capabilities = config.get("capabilities", [])
        if (
            connector == ConnectorType.Ticketing
            and "create_attachment" in capabilities
            and "download_attachment" in capabilities
        ):
            sync_attachments.append(integration_name)
    if connector.lower() == ConnectorType.Edr.lower():
        description = f"Sync endpoints, apps, and alerts data between {', '.join(integrations)} and RegScale data."
    else:
        description = f"Sync {connector.capitalize()} data between {', '.join(integrations)} and RegScale data."
    if sync_attachments:
        description += f" You are also able to sync attachments between {', '.join(sync_attachments)} and RegScale."
    return description


def _build_op_kwargs_and_docstring(
    config: dict, integration: str, param_type: str, op_kwargs: str, doc_string: str, capabilities: list[str]
) -> tuple[str, str]:
    """
    Build the op_kwargs and docstring for the DAG

    :param dict config: The config for the integration
    :param str integration: The name of the integration, typically connector_integration
    :param str param_type: The type of parameter to build
    :param str op_kwargs: The op_kwargs to add to the DAG
    :param str doc_string: The docstring to add to the DAG
    :param list[str] capabilities: The capabilities of the integration
    :return: The op_kwargs and docstring
    :rtype: tuple[str, str]
    """
    proper_type = param_type.replace("_", " ").title()
    op_kwargs, doc_string = _build_expected_params(
        param_type=param_type,
        integration=integration,
        op_kwargs=op_kwargs,
        doc_string=doc_string,
        capabilities=capabilities,
    )

    if ConnectorType.Vulnerabilities.lower() in integration and param_type == "optional_params":
        if param_type == "optional_params" and ConnectorType.Vulnerabilities in integration:
            vuln_params: dict[str, Param] = {
                "vuln_filter": Param(
                    name="vuln_filter",
                    type="choice",
                    description="Filter the vulnerabilities for the selected severity. (Options: critical, high, medium, low, info)",
                    default=None,
                ),
                "scan_date": Param(
                    name="scan_date",
                    type="string",
                    description="The date of the scan to sync vulnerabilities into RegScale.",
                    default="Critical",
                ),
                "all_scans": Param(
                    name="all_scans",
                    type="boolean",
                    description="Whether to sync all vulnerabilities into RegScale.",
                    default=False,
                ),
            }
            config[param_type] = {**config[param_type], **vuln_params}
    if config.get(param_type):
        if proper_type not in doc_string:
            doc_string += f"{proper_type}:\n"
        for param in config[param_type]:
            op_kwargs, doc_string = _build_other_params(
                config=config,
                param=param,
                param_type=param_type,
                proper_type=proper_type,
                integration=integration,
                op_kwargs=op_kwargs,
                doc_string=doc_string,
            )
    return op_kwargs, doc_string


def _build_expected_params(
    param_type: str, integration: str, op_kwargs: str, doc_string: str, capabilities: list[str]
) -> tuple[str, str]:
    """
    Build the expected params for the DAG and add them to the op_kwargs and docstring

    :param str param_type: The type of parameter to build
    :param str integration: The name of the integration, typically connector_integration
    :param str op_kwargs: The op_kwargs to add to the DAG
    :param str doc_string: The docstring to add to the DAG
    :param list[str] capabilities: The capabilities of the integration
    :return: The op_kwargs and docstring
    :rtype: tuple[str, str]
    """
    if param_type == "expected_params" and ConnectorType.Ticketing in integration:
        regscale_id_jinja = "'regscale_id'"
        regscale_module_jinja = "'regscale_module'"
        op_kwargs += f'\n        "regscale_id": "{{{{ dag_run.conf[{regscale_id_jinja}] }}}}",'
        op_kwargs += f'\n        "regscale_module": "{{{{ dag_run.conf[{regscale_module_jinja}] }}}}",'
        doc_string += "Expected Params:\n"
        doc_string += "    regscale_id: INTEGER ID from RegScale of the RegScale object\n"
        doc_string += "    regscale_module: STRING name of the RegScale module to use with the provided ID\n"
        op_kwargs, doc_string = add_connector_specific_params(capabilities, integration, op_kwargs, doc_string)
    elif param_type == "expected_params":
        regscale_ssp_id_jinja = "'regscale_ssp_id'"
        op_kwargs += f'\n        "regscale_ssp_id": "{{{{ dag_run.conf[{regscale_ssp_id_jinja}] }}}}",'
        doc_string += "Expected Params:\n"
        doc_string += "    regscale_ssp_id: INTEGER ID from RegScale of the System Security Plan\n"
        op_kwargs, doc_string = add_connector_specific_params(capabilities, integration, op_kwargs, doc_string)
    return op_kwargs, doc_string


def _build_other_params(
    config: dict, param: str, param_type: str, proper_type: str, integration: str, op_kwargs: str, doc_string: str
) -> tuple[str, str]:
    """
    Build the other params for the DAG by adding them to the op_kwargs and docstring

    :param str param_type: The type of parameter to build
    :param str integration: The name of the integration, typically connector_integration
    :param str op_kwargs: The op_kwargs to add to the DAG
    :param str doc_string: The docstring to add to the DAG
    :return: The op_kwargs and docstring
    :rtype: tuple[str, str]
    """
    param_obj: Param = config[param_type][param]
    param_name = f"{integration.lower()}_{param}" if param_type == "required_secrets" else param
    jinja_key = f"'{param_name}'"
    if default := param_obj.default:
        if param_obj.data_type.lower() == "str":
            jinja_default = f"'{default}'"
        else:
            jinja_default = default
    else:
        jinja_default = None
    if param_type == "optional_params":
        op_kwargs += f'\n        "{param_name}": "{{{{ dag_run.conf[{jinja_key}] if {jinja_key} in dag_run.conf else {jinja_default} }}}}",'
        doc_string += f"    {param_name}: {param_obj.expected_type.upper()} {param_obj.description} {f'(Default: {param_obj.default})' if 'Options' not in param_obj.description else ''}\n"
    else:
        op_kwargs += f'\n        "{param_name}": "{{{{ dag_run.conf[{jinja_key}] }}}}",'
        doc_string += f"    {param_name}: {param_obj.expected_type.upper()} {param_obj.description or proper_type}\n"
    return op_kwargs, doc_string


def add_connector_specific_params(
    capabilities: list[str], integration: str, op_kwargs: str, doc_string: str
) -> tuple[str, str]:
    """
    Updated the op_kwargs and docstring for the DAG to include specific params for the connector based on capabilities

    :param list[str] capabilities: The capabilities of the integration
    :param str integration: The name of the integration, typically connector_integration
    :param str op_kwargs: The op_kwargs to add to the DAG
    :param str doc_string: The docstring to add to the DAG
    :return: The updated op_kwargs and docstring
    :rtype: tuple[str, str]
    """
    if (
        ConnectorType.Ticketing in integration
        and "create_attachment" in capabilities
        and "download_attachment" in capabilities
    ):
        sync_attachments_jinja = "'sync_attachments'"
        op_kwargs += f'\n        "sync_attachments": "{{{{ dag_run.conf[{sync_attachments_jinja}] if {sync_attachments_jinja} in dag_run.conf else False }}}}",'
        doc_string += "    sync_attachments: BOOLEAN Whether to sync attachments between integration and RegScale\n"
    return op_kwargs, doc_string


def generate_click_connectors() -> None:
    """Generate Click Connectors for the RegScale CLI"""
    from regscale.core.app.utils.app_utils import check_file_path
    from regscale.models.integration_models.synqly_models.synqly_model import SynqlyModel

    model = SynqlyModel()
    configs = model._get_integrations_and_secrets(True)
    # iterate through connectors and generate DAGs
    for connector in SUPPORTED_CONNECTORS:
        save_dir = "regscale/integrations/commercial/synqly"
        check_file_path(save_dir)
        connector_configs = {
            integration: configs[integration] for integration in configs if connector in integration.lower()
        }
        # sort the connector configs by the key for repeatability
        connector_configs = dict(sorted(connector_configs.items()))
        # check airflow/dags for existing DAGs and skip them
        _create_and_save_click_command(
            model=model,
            connector=connector,
            integration_configs=connector_configs,
            save_dir=save_dir,
        )
        # add the new click group to regscale.py
        _add_command_to_regscale(connector)


def _create_and_save_click_command(
    model: "SynqlyModel", connector: str, integration_configs: dict[str, dict], save_dir: str
) -> None:
    """
    Create and save a click command for the given integration and connector

    :param SynqlyModel model: The model to use for the DAG
    :param str connector: The connector type to create click commands for
    :param dict[str, dict] integration_configs: Dictionary containing the integration configs for the given connector
    :param str save_dir: The directory to save the DAG to
    :rtype: None
    """
    integrations_count = 0
    doc_string = f"{connector.capitalize()} connector commands for the RegScale CLI"
    if connector == ConnectorType.Ticketing:
        import_command = "from regscale.models import regscale_id, regscale_module"
    elif connector == ConnectorType.Vulnerabilities:
        import_command = "from datetime import datetime\nfrom regscale.models import regscale_ssp_id"
    else:
        import_command = "from regscale.models import regscale_ssp_id"
    # this indent is important to keep the code valid python
    cli_code = f"""
\"\"\"{doc_string}\"\"\"\n
import click
{import_command}


@click.group()
def {connector}() -> None:
    \"\"\"{doc_string}\"\"\"
    pass
"""

    # replace the integration config with a flattened version
    for integration, config in integration_configs.items():
        capabilities = config.get("capabilities", [])
        integration_name = integration[integration.find("_") + 1 :]
        config = model._flatten_secrets(integration=integration, return_secrets=True)
        click_options_and_command = _build_click_options_and_command(
            config=config,
            connector=connector,
            integration_name=integration_name,
            capabilities=capabilities,
        )
        cli_code += f"\n\n{click_options_and_command}"
        integrations_count += 1

    with open(f"{save_dir}/{connector.lower()}.py", "w") as f:
        f.write("# flake8: noqa E501\n# pylint: disable=line-too-long\n")
        f.write(cli_code)
        f.write("# pylint: enable=line-too-long\n")
    print(f"Generated click commands for {integrations_count} {connector} connector(s).")


def _build_all_params(integration_name: str, connector: str) -> tuple[list[str], list[str], list[str]]:
    """
    Function to build the click options, function params, and function kwargs for the integration

    :param str integration_name: The name of the integration
    :param str connector: The connector type
    :return: The click options, function params, and function kwargs
    :rtype: tuple[list[str], list[str], list[str]]
    """
    if connector == ConnectorType.Vulnerabilities:
        vuln_filter_option = "@click.option(\n    '--vuln_filter',\n    help='Filter the vulnerabilities for the selected severity. (Options: critical, high, medium, low, info)',\n    required=False,\n    type=click.Choice(['critical', 'high', 'medium', 'low', 'info']),\n    default=None)\n"
        scan_date_option = f"@click.option(\n    '--scan_date',\n    help='The date of the scan to sync vulnerabilities from {integration_name}',\n    required=False,\n    type=click.DateTime(formats=['%Y-%m-%d']),\n    default=None)\n"
        all_vulns_flag = f"@click.option(\n    '--all_scans',\n    help='Whether to sync all vulnerabilities from {integration_name}',\n    required=False,\n    is_flag=True,\n    default=False)\n"
        click_options = ["@regscale_ssp_id()", vuln_filter_option, scan_date_option, all_vulns_flag]
        function_params = ["regscale_ssp_id: int", "vuln_filter: str", "scan_date: datetime", "all_scans: bool"]
        function_kwargs = [
            "regscale_ssp_id=regscale_ssp_id",
            "vuln_filter=vuln_filter",
            "scan_date=scan_date",
            "all_scans=all_scans",
        ]
    elif connector == ConnectorType.Ticketing:
        click_options = ["@regscale_id()", "@regscale_module()"]
        function_params = ["regscale_id: int", "regscale_module: str"]
        function_kwargs = ["regscale_id=regscale_id", "regscale_module=regscale_module"]
    else:
        click_options = ["@regscale_ssp_id()"]
        function_params = ["regscale_ssp_id: int"]
        function_kwargs = ["regscale_ssp_id=regscale_ssp_id"]
    return click_options, function_params, function_kwargs


def _build_click_options_and_command(
    config: dict, connector: str, integration_name: str, capabilities: list[str]
) -> str:
    """
    Function to use the config to build the click options and command for the integration

    :param dict config: The config for the integration
    :param str connector: The connector type
    :param str integration_name: The name of the integration
    :param list[str] capabilities: The capabilities of the integration
    :return: The click options as a string
    :rtype: str
    """
    doc_string_name = integration_name.replace("_", " ").title()
    # add regscale_ssp_id as a default option
    click_options, function_params, function_kwargs = _build_all_params(doc_string_name, connector)
    for param_type in ["expected_params", "optional_params"]:
        for param in config.get(param_type, []):
            param_data = config[param_type][param]
            if not param_data.click_type:
                continue
            # indentation is important to keep the code valid python
            click_option = f"""@click.option(
    '--{param}',
    type={param_data.click_type},
    help='{config[param_type][param].description}',
    required={not param_data.optional},
    {"prompt='" + config[param_type][param].description + "'," if not param_data.optional else ""}
)"""
            function_params.append(f"{param}: {param_data.data_type}")
            function_kwargs.append(f"{param}={param}")
            click_options.append(click_option)
    if (
        ConnectorType.Ticketing == connector
        and "create_attachment" in capabilities
        and "download_attachment" in capabilities
    ):
        click_options.append(
            f"""@click.option(
    '--sync_attachments',
    type=click.BOOL,
    help='Whether to sync attachments between {doc_string_name} and RegScale',
    required=False,
    default=True,
)"""
        )
        function_params.append("sync_attachments: bool")
        function_kwargs.append("sync_attachments=sync_attachments")
    click_options = "\n".join(click_options)
    function_params = ", ".join(function_params)
    # indentation is important to keep the code valid python
    click_command = f"""@{connector}.command(name="sync_{integration_name}")
{click_options}
def sync_{integration_name}({function_params}) -> None:
    \"\"\"Sync {connector.title()} {"data between" if connector == ConnectorType.Ticketing else "from"} {doc_string_name} {"and" if connector == ConnectorType.Ticketing else "to"} RegScale.\"\"\"
    from regscale.models.integration_models.synqly_models.connectors import {connector.title()}
    {connector}_{integration_name} = {connector.title()}('{integration_name}')
    {connector}_{integration_name}.run_sync({', '.join(function_kwargs)})
"""
    return click_command


def _add_command_to_regscale(connector: str) -> None:
    """
    Add the new click group and command to the regscale.py file

    :param str connector: The connector type
    :rtype: None
    """
    import_section = 'burp = import_command_with_timing(COMMERCIAL, "burp")'
    command_section = "cli.add_command(burp)  # add Burp File Integration"
    with open("regscale/regscale.py", "r") as f:
        regscale_code = f.read()
    if f"{connector} =" in regscale_code:
        print(f"{connector.title()} click commands already exists in regscale.py.")
        return
    import_line = f'{connector} = import_command_with_timing("regscale.integrations.commercial.synqly.{connector}", "{connector}")'
    regscale_code = regscale_code.replace(import_section, f"{import_section}\n{import_line}")
    regscale_code = regscale_code.replace(
        command_section, f"{command_section}\ncli.add_command({connector})  # add {connector.capitalize()} connector"
    )
    with open("regscale/regscale.py", "w") as f:
        f.write(regscale_code)
    print(f"Added {connector} click group to regscale.py.")
