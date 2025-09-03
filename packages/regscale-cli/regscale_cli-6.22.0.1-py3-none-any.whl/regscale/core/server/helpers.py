"""Helper functions for the CLI API Wrapper"""

import os
from contextlib import redirect_stdout, suppress
from io import StringIO
from typing import Callable, Dict, Optional, Tuple, Union, List
from urllib.parse import urljoin

from click import Argument, Command, Context, Option
from flask import url_for
from flask_restx import Api, Model, Resource, fields
from flask_restx.reqparse import RequestParser
from requests.exceptions import JSONDecodeError
from requests.models import ReadTimeoutError

from regscale.core.app.api import Api as CliApi
from regscale.core.app.application import Application
from regscale.utils.string import remove_ansi_escape_sequences

GET_OPTIONS = "GET, OPTIONS"
POST_OPTIONS = "POST, OPTIONS"
ALLOWED_METHODS = "Allowed methods"


def execute_click_command_in_context(command: Command, params: dict = None) -> str:
    """Execute a click command

    :param Command command: a click.Command for performing the logic
    :param dict params: an optional dictionary of parameter key values to pass, defaults to None
    :return: a string of the command output
    :rtype: str
    """
    with Context(command) as ctx:
        # redirect stdout to a string to capture command output
        output_stream = StringIO()
        with redirect_stdout(output_stream):
            with suppress(SystemExit):
                if params:
                    # run command, params are key values of the request JSON
                    ctx.invoke(command, **params)
                else:
                    # no params, so don't use them
                    ctx.invoke(command)
            # retrieve the output, remove ansi escape sequences to not color
            # also remove trailing returns
            output = remove_ansi_escape_sequences(text=output_stream.getvalue().strip())
    return output


# pylint: disable=duplicate-code
def create_view_func(command: Command) -> Union[Callable, Resource]:
    """Create a factory function for returning a CommandResource object for use in an API.

    :param Command command: a click.Command for performing the logic
    :return: a Resource instance
    :rtype: Union[Callable, Resource]
    """
    parser = RequestParser()
    for param in command.params:
        parser.add_argument(param.human_readable_name, type=param.type, location="json")

    # define a CommandResource class to return (get or post depending upon if params are expected)
    if command.params and all([param.required for param in command.params]):

        class CommandResource(Resource):
            """Allow for the use of this view function using flask_restx."""

            def options(self) -> dict:
                """Return the allowed methods and any parameters expected"""
                methods = GET_OPTIONS if not command.params else POST_OPTIONS
                return {
                    ALLOWED_METHODS: methods,
                    "Parameters": [param.human_readable_name for param in command.params],
                }

            def post(self) -> Tuple[Dict[str, str], int]:
                """Return output with params in a POST request"""
                if not command.params:
                    return {
                        "message": "Invalid method. This endpoint does not accept parameters, use GET method instead"
                    }, 405
                args = parser.parse_args()
                params = {k: v for k, v in args.items() if v is not None}
                output = execute_click_command_in_context(command, params)
                return {"input": f"regscale {command.name}", "output": output}, 200

    elif command.params:

        class CommandResource(Resource):
            """Allow for the use of this view function using flask_restx."""

            def options(self) -> dict:
                """Return the allowed methods and any parameters expected"""
                methods = GET_OPTIONS if not command.params else POST_OPTIONS
                return {
                    ALLOWED_METHODS: methods,
                    "Parameters": [param.human_readable_name for param in command.params],
                }

            def post(self) -> Tuple[Dict[str, str], int]:
                """Return output with params in a POST request"""
                if not command.params:
                    return {
                        "message": "Invalid method. This endpoint does not accept parameters, use GET method instead"
                    }, 405
                args = parser.parse_args()
                params = {k: v for k, v in args.items() if v is not None}
                output = execute_click_command_in_context(command, params)
                return {"input": f"regscale {command.name}", "output": output}, 200

            def get(self) -> Tuple[Dict[str, str], int]:
                """Return output if get command is invoked."""
                if command.params:
                    return {
                        "message": "Invalid method. This endpoint expects parameters "
                        "use POST method for this endpoint with the following parameters: "
                        f"{','.join([p.human_readable_name for p in command.params])}",
                    }, 405
                output = execute_click_command_in_context(command)
                return {"input": f"regscale {command.name}", "output": output}, 200

    else:

        class CommandResource(Resource):
            """Allow for the use of this view function using flask_restx."""

            def options(self) -> dict:
                """Return the allowed methods and any parameters expected"""
                methods = GET_OPTIONS if not command.params else POST_OPTIONS
                return {
                    ALLOWED_METHODS: methods,
                    "Parameters": [param.human_readable_name for param in command.params],
                }

            def get(self) -> Tuple[Dict[str, str], int]:
                """Return output if get command is invoked."""
                if command.params:
                    return {
                        "message": "Invalid method. This endpoint expects parameters "
                        "use POST method for this endpoint with the following parameters: "
                        f"{','.join([p.human_readable_name for p in command.params])}",
                    }, 405
                output = execute_click_command_in_context(command)
                return {"input": f"regscale {command.name}", "output": output}, 200

    return CommandResource


# pylint: enable=duplicate-code


def _get_field_type(param: Union[Option, Argument]) -> fields.Raw:
    """Retrieve the field type from a click.Option or click.Argument

    :param Union[Option, Argument] param: a click.Option or click.Argument
    :return: a flask_restx.fields type
    :rtype: fields.Raw
    """
    if param.type == int:
        return fields.Integer
    if param.type == float:
        return fields.Float
    if param.type == bool:
        return fields.Boolean
    return fields.String


def generate_parameters_model(api_instance: Api, command: Command) -> Model:
    """Generate a Flask_restx parameter model

    :param Api api_instance: the flask_restx.Api instance
    :param Command command: a click.Command to retrieve a Model from
    :return: a flask_restx.Model of the parameters
    :rtype: Model
    """
    parameters = {}
    for param in command.params:
        field_type = _get_field_type(param)
        parameters[param.name] = field_type(required=param.required, description=param.help)
    return api_instance.model(f"{command.name.title().replace('_', '')}Parameters", parameters)


def get_site_info() -> Dict:
    """Get site info

    :return: Dictionary of site information to pass into pages
    :rtype: Dict
    """
    app = Application()
    site_info = {"domain": os.getenv("REGSCALE_DOMAIN", app.config["domain"])}

    return site_info


def get_catgalogues() -> List[Tuple[int, str]]:
    """Get catalogues information

    :return: List of tuples of catalogs in RegScale instance
    :rtype: List[Tuple[int, str]]
    """
    cli_app = Application()
    api = CliApi(cli_app)
    try:
        response = api.get(f"{cli_app.config['domain']}/api/catalogues/getlist")
        catalog_data = response.json()
        regscale_catalogues = [
            (catalog["id"], f'{catalog["title"][:45]} (#{catalog["id"]})') for catalog in catalog_data
        ]
    except (JSONDecodeError, KeyError, AttributeError, TypeError):
        regscale_catalogues = [
            (1, "Please Login to RegScale to retrieve Catalogues."),
        ]
    return sorted(regscale_catalogues, key=lambda x: x[1])


def get_ssps() -> List[Tuple[int, str]]:
    """Get Security Plans from RegScale instance

    :return: List of tuples of catalogs in RegScale instance
    :rtype: List[Tuple[int, str]]
    """
    cli_app = Application()
    api = CliApi(cli_app)
    body = """
            query {
                securityPlans(take: 50, skip: 0) {
                items {
                    id
                    systemName
                },
                pageInfo {
                    hasNextPage
                }
                ,totalCount}
            }
        """
    try:
        response = api.graph(query=body)
        ssp_data = response["securityPlans"]["items"]
        regscale_ssps = [(ssp["id"], f'{ssp["systemName"][:45]} (#{ssp["id"]})') for ssp in ssp_data]
    except (JSONDecodeError, KeyError, AttributeError, TypeError):
        regscale_ssps = [
            (1, "Please Login to RegScale to retrieve SSPs."),
        ]
    return regscale_ssps


def get_ssp_name(ssp_id: Union[str, int]) -> str:
    """Get Security Plans from RegScale instance

    :param Union[str, int] ssp_id: ID of SSP to retrieve name for
    :return: Name of the SSP from RegScale
    :rtype: str
    """
    cli_app = Application()
    api = CliApi(cli_app)
    body = f"""
            query {{
                securityPlans(take: 50, skip: 0, where: {{id: {{eq: {ssp_id}}}}}) {{
                items {{
                    id
                    systemName
                }},
                pageInfo {{
                    hasNextPage
                }}
                ,totalCount}}
            }}
            """
    try:
        response = api.graph(query=body)
        ssp_name = response["securityPlans"]["items"][0]["systemName"]
    except (JSONDecodeError, KeyError, AttributeError, TypeError, ReadTimeoutError):
        ssp_name = f"RegScale SSP# {ssp_id}"
    return ssp_name


def delete_all_items_in_directory(dir_path: str, keep_ext: Optional[str] = None) -> None:
    """
    Recursively delete all files and directories in the given directory

    :param str dir_path: The directory whose contents are to be deleted
    :param Optional[str] keep_ext: The file extension to keep (g.g., '.ckl') If None, all files will be deleted
    :rtype: None
    """
    # Check if the directory exists
    if not os.path.exists(dir_path):
        print(f"The directory {dir_path} does not exist.")
        return

    # Iterate through all the items in the directory
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)

        # If item is a directory, recursively call this function
        if os.path.isdir(item_path):
            delete_all_items_in_directory(item_path, keep_ext)

            # Remove the directory only if it's empty
            if not os.listdir(item_path):
                os.rmdir(item_path)

        else:
            check_ext(keep_ext, item_path)


def check_ext(keep_ext: Optional[str], item_path: str) -> None:
    """
    Check if the file extension should be kept or removed

    :param Optional[str] keep_ext: The file extension to keep (g.g., '.ckl') If None, all files will be deleted
    :param str item_path: The path of the file to check
    """
    # If keep_ext is None, remove all files
    if keep_ext is None:
        os.remove(item_path)
    else:
        # Otherwise, get the file extension and check if it should be kept
        _, ext = os.path.splitext(item_path)
        if ext != keep_ext:
            os.remove(item_path)


def get_profiles() -> List[Tuple[int, str]]:
    """Get catalogues information

    :return: List of tuples of catalogs in RegScale instance
    :rtype: List[Tuple[int, str]]
    """
    cli_app = Application()
    api = CliApi(cli_app)
    response = api.get(urljoin(cli_app.config["domain"], "/api/profiles/getlist"))
    try:
        profiles = response.json()
        regscale_profiles = [(profile["id"], f'{profile["name"][:45]} (#{profile["id"]})') for profile in profiles]
    except (JSONDecodeError, KeyError, AttributeError, TypeError, ReadTimeoutError):
        regscale_profiles = [
            (1, "Please Login to RegScale to retrieve Profiles."),
        ]
    return sorted(regscale_profiles, key=lambda x: x[1])


def generate(app, file_path, filename, catalogue_id):
    """
    Generate the HTML content for processing the SSP
    """
    # Push/flush content to browser
    yield "<html><head><title>Processing SSP</title></head><body>"
    yield "<h1>Processing Security Plan</h1>"

    with app.test_request_context() as context:
        from regscale.integrations.public.fedramp.import_fedramp_r4_ssp import parse_and_load_xml_rev4

        # Call the existing function and get the CSV path and results
        parse_and_load_gen = parse_and_load_xml_rev4(
            context, file_path=file_path, filename=filename, catalogue_id=catalogue_id
        )

        csv_path, result_output, implementation_results = None, None, None
        # Yield from the generator returned by parse_and_load_xml_rev4
        for content in parse_and_load_gen:
            if isinstance(content, tuple):
                csv_path, result_output, implementation_results = content
            else:
                yield content

        if csv_path and result_output and implementation_results:
            final_results_url = url_for(
                "final_results", csv_path=csv_path, result_output=result_output, filename=filename
            )
            # yield a javascript re-direct to the browser to clear progress content and load result page
            yield f'<script>window.location.href = "{final_results_url}";</script>'
        yield "</body></html>"
