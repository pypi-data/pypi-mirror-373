#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main script for starting RegScale CLI application"""
# standard python imports
import logging
import os
import sys

# Initialize config from AWS Secrets Manager if running in container
secret_name = os.getenv("SECRET_NAME")
if os.getenv("REGSCALE_CONTAINER") == "Yes" and secret_name:
    try:
        import boto3

        session = boto3.session.Session()
        client = session.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_name)
        secret = response["SecretString"]

        # Write the secret to init.yaml
        config_path = "/tmp/init.yaml"
        with open(config_path, "w") as f:
            f.write(secret)

        # Set the config path environment variable
        os.environ["REGSCALE_CONFIG"] = config_path

        logging.info(f"Loaded configuration from AWS Secrets Manager: {secret_name}")
    except Exception as e:
        logging.error(f"Failed to load secret from AWS Secrets Manager: {str(e)}")
        sys.exit(1)

# flake8: noqa: E402
import time
from getpass import getpass
from typing import Any, Optional
from urllib.parse import urlparse

import click
import psutil
from rich.console import Console

from regscale.models.app_models.click import NotRequiredIf, regscale_id, regscale_module

if working_dir := os.getenv("REGSCALE_WORKDIR"):
    os.chdir(working_dir)

start_time = time.time()  # noqa
import importlib

############################################################
# Internal Integrations
############################################################
import regscale.core.app.internal.healthcheck as hc
import regscale.core.app.internal.login as lg

############################################################
# Versioning
############################################################
from regscale import __version__
from regscale.core.app import create_logger

logger = create_logger()


def import_command_with_timing(
    module_name: str, command_name: str, warning_time_threshold: int = 0.02, warning_memory_threshold: int = 10.0
) -> Any:
    """
    Import a command from a module and log a warning if the import takes longer than the threshold

    :param str module_name: The name of the module to import the command from
    :param str command_name: The name of the command to import
    :param int warning_time_threshold: The threshold in seconds for logging a warning if the import takes longer, default is 0.02 seconds
    :param int warning_memory_threshold: The threshold in MB for logging a warning if the memory increase is greater than the threshold, default is 10.0 MB    :return: The command object imported from the module
    :raises ImportError: If the command is not found in the module
    :return: The command object imported from the module
    :rtype: Any
    """
    if logger.getEffectiveLevel() == logging.DEBUG:
        before_import = set(sys.modules.keys())
        memory_before = psutil.Process().memory_info().rss / (1024 * 1024)  # Memory in MB

        start_time = time.time()
        module = importlib.import_module(module_name)
        command = getattr(module, command_name, None)
        elapsed_time = time.time() - start_time

        after_import = set(sys.modules.keys())
        new_modules = after_import - before_import
        memory_after = psutil.Process().memory_info().rss / (1024 * 1024)  # Memory in MB

        if elapsed_time > warning_time_threshold or memory_after - memory_before > warning_memory_threshold:
            logger.debug(f"Warning: Importing {command_name} from {module_name} took {elapsed_time} seconds to import!")
            logger.debug(f"New modules loaded during import: {new_modules}")
            logger.debug(f"Memory used after import: {memory_after:.2f} MB")
            logger.debug(f"Memory increase: {(memory_after - memory_before):.2f} MB")
            logger.debug("--------------------------------------------------")
    else:
        start_time = time.time()
        module = importlib.import_module(module_name)
        command = getattr(module, command_name, None)
        elapsed_time = time.time() - start_time
        if elapsed_time > 0.01 and logger.level >= logging.DEBUG:
            logger.debug(f"Warning: Importing {command_name} from {module_name} took {elapsed_time} seconds to import!")

    if command is None:
        raise ImportError(f"No command named '{command_name}' found in '{module_name}'.")
    return command


############################################################
# Application Integrations
############################################################
ENCRYPT = "regscale.core.app.internal.encrypt"
INTERNAL = "regscale.core.app.internal"
actions = import_command_with_timing(INTERNAL, "admin_actions")
assessments = import_command_with_timing(INTERNAL, "assessments")
catalog = import_command_with_timing(INTERNAL, "catalog")
compare = import_command_with_timing(INTERNAL, "compare")
control_editor = import_command_with_timing(INTERNAL, "control_editor")
IOA21H98 = import_command_with_timing(ENCRYPT, "IOA21H98")
JH0847 = import_command_with_timing(ENCRYPT, "JH0847")
YO9322 = import_command_with_timing(ENCRYPT, "YO9322")
evidence = import_command_with_timing(INTERNAL, "evidence")
file_upload = import_command_with_timing("regscale.core.app.internal.file_uploads", "file_upload")
migrations = import_command_with_timing(INTERNAL, "migrations")
model = import_command_with_timing(INTERNAL, "model")
issues = import_command_with_timing(INTERNAL, "issues")
set_permissions = import_command_with_timing(INTERNAL, "set_permissions")

############################################################
# Public Integrations
############################################################
PUBLIC = "regscale.integrations.public"
alienvault = import_command_with_timing(PUBLIC, "alienvault")
cisa = import_command_with_timing(PUBLIC, "cisa")
csam = import_command_with_timing(PUBLIC, "csam")
emass = import_command_with_timing(PUBLIC, "emass")
fedramp = import_command_with_timing(PUBLIC, "fedramp")
nist = import_command_with_timing(PUBLIC, "nist")
oscal = import_command_with_timing(PUBLIC, "oscal")
criticality_updater = import_command_with_timing(PUBLIC, "criticality_updater")

############################################################
# Commercial Integrations
############################################################
COMMERCIAL = "regscale.integrations.commercial"
ad = import_command_with_timing(COMMERCIAL, "ad")
aqua = import_command_with_timing(COMMERCIAL, "aqua")
awsv2 = import_command_with_timing(COMMERCIAL, "aws")
azure = import_command_with_timing(COMMERCIAL, "azure")
burp = import_command_with_timing(COMMERCIAL, "burp")
edr = import_command_with_timing("regscale.integrations.commercial.synqly.edr", "edr")
assets = import_command_with_timing("regscale.integrations.commercial.synqly.assets", "assets")
vulnerabilities = import_command_with_timing(
    "regscale.integrations.commercial.synqly.vulnerabilities", "vulnerabilities"
)
ticketing = import_command_with_timing("regscale.integrations.commercial.synqly.ticketing", "ticketing")
crowdstrike = import_command_with_timing(COMMERCIAL, "crowdstrike")
defender = import_command_with_timing(COMMERCIAL, "defender")
dependabot = import_command_with_timing(COMMERCIAL, "dependabot")
durosuite = import_command_with_timing(COMMERCIAL + ".durosuite.scanner", "durosuite")
ecr = import_command_with_timing(COMMERCIAL, "ecr")
gcp = import_command_with_timing(COMMERCIAL, "gcp")
gitlab = import_command_with_timing(COMMERCIAL, "gitlab")
ibm = import_command_with_timing(COMMERCIAL, "ibm")
import_all = import_command_with_timing(COMMERCIAL, "import_all")
jira = import_command_with_timing(COMMERCIAL, "jira")
nexpose = import_command_with_timing(COMMERCIAL, "nexpose")
okta = import_command_with_timing(COMMERCIAL, "okta")
prisma = import_command_with_timing(COMMERCIAL, "prisma")
qualys = import_command_with_timing(COMMERCIAL, "qualys")
salesforce = import_command_with_timing(COMMERCIAL, "salesforce")
sap = import_command_with_timing("regscale.integrations.commercial.sap.click", "sap")
sysdig = import_command_with_timing("regscale.integrations.commercial.sap.sysdig.click", "sysdig")
servicenow = import_command_with_timing(COMMERCIAL, "servicenow")
sicura = import_command_with_timing(COMMERCIAL, "sicura")
stig_mapper = import_command_with_timing(COMMERCIAL, "stig_mapper")
stig = import_command_with_timing(COMMERCIAL, "stig")
snyk = import_command_with_timing(COMMERCIAL, "snyk")
sonarcloud = import_command_with_timing(COMMERCIAL, "sonarcloud")
tenable = import_command_with_timing(COMMERCIAL, "tenable")
trivy = import_command_with_timing(COMMERCIAL, "trivy")
grype = import_command_with_timing(COMMERCIAL, "grype")
veracode = import_command_with_timing(COMMERCIAL, "veracode")
wiz = import_command_with_timing(COMMERCIAL, "wiz")
xray = import_command_with_timing(COMMERCIAL, "xray")
fortify = import_command_with_timing(COMMERCIAL, "fortify")

logger = logging.getLogger("regscale")


@click.group()
@click.option(
    "--config",
    type=click.STRING,
    help="Config to use for the CLI. Can be a JSON string or a path to a YAML/JSON file",
    default=None,
    hidden=True,
)
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.version_option(
    __version__,
    "--version",
    "-V",
    prog_name="RegScale CLI",
)
@click.pass_context
def cli(ctx, config, debug) -> click.Group:
    """
    Welcome to the RegScale CLI client app!
    """
    # Ensure that ctx.obj exists and is a dict (in case further commands need to pass more data)
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug

    if config:
        import json
        import yaml
        from regscale.core.app.application import Application

        try:
            try:
                # First try to parse as JSON string
                ctx.obj["CONFIG"] = json.loads(config)
            except json.JSONDecodeError:
                # If not JSON, try as file path
                if os.path.isfile(config):
                    with open(config, "r") as f:
                        if config.endswith(".json"):
                            ctx.obj["CONFIG"] = json.load(f)
                        else:
                            ctx.obj["CONFIG"] = yaml.safe_load(f)
                else:
                    logger.error(f"Config must be valid JSON string or path to JSON/YAML file path: {config}")
                    ctx.obj["CONFIG"] = {}
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}, using default config.")
            ctx.obj["CONFIG"] = {}

    if debug:
        logger.setLevel("DEBUG")


# About function
@cli.command()
def about():
    """Provides information about the CLI and its current version."""
    banner()
    about_display()


@cli.command(hidden=True)
def import_time():
    """Displays the total import time for the CLI."""
    end_time = time.time()
    console = Console()
    console.print(f"Total Import Time: {end_time - start_time} seconds")


def about_display():
    """Provides information about the CLI and its current version."""
    console = Console()
    console.print(f"[red]RegScale[/red] CLI Version: {__version__}")
    console.print("Author: J. Travis Howerton (thowerton@regscale.com)")
    console.print("Copyright: RegScale Incorporated")
    console.print("Pre-Requisite: Python 3.9, 3.10, 3.11, 3.12, or 3.13")
    console.print("Website: https://www.regscale.com")
    console.print("Read the CLI Docs: https://regscale.readme.io/docs/overview")
    console.print(
        "\n[red]DISCLAIMER: RegScale does not conduct any form of security scanning for data imported by the customer. "
        + "It is the customer's responsibility to ensure that data imported into the platform using "
        + "the Command Line Interface meets industry standard, minimum security screening requirements. "
        + "RegScale has no liability for failing to scan any such data or for any data imported by "
        + "the customer that fails to meet such requirements.[red]\n"
    )


def banner():
    """RegScale logo banner"""
    txt = """
\t[#10c4d3] .';;;;;;;;;;;;;[#14bfc7];;;;;;;;;;;;,'..
\t[#10c4d3].:llllllllllllll[#14bfc7]lllllllllllllllc:'.
\t[#10c4d3].cliclicliclicli[#14bfc7]clicliclicliclooool;.
\t[#10c4d3].cliclic###################;:looooooc'
\t[#05d1b7].clicli,                     [#15cfec].;loooool'
\t[#05d1b7].clicli,                       [#18a8e9].:oolloc.
\t[#05d1b7].clicli,               [#ef7f2e].,cli,.  [#18a8e9].clllll,
\t[#05d1b7].clicli.             [#ef7f2e].,oxxxxd;  [#158fd0].:lllll;
\t[#05d1b7] ..cli.            [#f68d1f]';cdxxxxxo,  [#18a8e9].cllllc,
\t                 [#f68d1f].:odddddddc.  [#1b97d5] .;ccccc:.
\t[#ffc42a]  ..'.         [#f68d1f].;ldddddddl'  [#0c8cd7].':ccccc:.
\t[#ffc42a] ;xOOkl.      [#e9512b]'coddddddl,.  [#0c8cd7].;::::::;.
\t[#ffc42a]'x0000O:    [#e9512b].:oooooool;.  [#0c8cd7].,::::::;'.
\t[#ffc42a]'xO00OO:  [#e9512b].;loooooo:,.  [#0c8cd7].';::;::;'.
\t[#ff9d20]'xOOOOOc[#ba1d49].'cllllllc'    [#0c83c8].,;;;;;;,.
\t[#ff9d20]'xOOOOOo[#ba1d49]:clllllc'.     [#0c83c8]';;;;;;'.
\t[#ff9d20]'xOOOOOd[#ba1d49]ccccc:,.       [#1a4ea4].',,,,'''.
\t[#ff9d20]'dOOOOkd[#ba1d49]c:::,.           [#1a4ea4]..''''''..
\t[#f68d1f]'dkkkkko[#ba1d49]:;,.               [#1a4ea4].''''','..
\t[#f68d1f]'dkkkkkl[#ba1d49],.                   [#0866b4].''',,,'.
\t[#f68d1f].lkkkkx;[#ba1d49].                     [#0866b4]..',,,,.
\t[#f68d1f] .;cc:'                         [#0866b4].....
 """
    console = Console()
    console.print(txt)


@cli.command("version")
@click.option("--server", is_flag=True, help="Display the version information from the server and exit.")
def version(server: bool = False) -> None:
    """
    Display the CLI or RegScale application version and exit.
    """
    if server:
        from urllib.parse import urljoin

        from regscale.core.app.api import Api

        api = Api()
        res = api.get(urljoin(api.app.config["domain"], "/assets/json/version.json"))
        if res and res.ok:
            try:
                print(res.json()["version"])
            except ValueError:
                print("Unable to get version from server.")
        else:
            print("Unable to get version from server.")
        sys.exit(0)
    print(__version__)


@cli.command(name="change_passkey")
def change_passkey():
    """Change your encryption/decryption passkey."""
    YO9322()
    sys.exit()


@cli.command()
@click.option("--file", hide_input=False, help="File to encrypt.", prompt=True, required=True)
def encrypt(file):
    """Encrypts .txt, .yaml, .json, & .csv files."""
    if file:
        JH0847(file)
        sys.exit()


@cli.command()
@click.option("--file", hide_input=False, help="File to decrypt.", prompt=True, required=True)
def decrypt(file):
    """Decrypts .txt, .yaml, .json, & .csv files."""
    if file:
        IOA21H98(file)
        sys.exit()


# Update config parameter
@cli.command()
@click.option(
    "--param",
    hide_input=False,
    help="CLI config parameter name.",
    prompt=True,
    required=True,
    type=click.STRING,
)
@click.option(
    "--val",
    hide_input=True,
    help="CLI config parameter value.",
    type=click.STRING,  # default is string even if entering an integer
    prompt=True,
    required=True,
)
def config(param, val):
    """Updates init.yaml config parameter with value"""
    # check if key provided exists in init.yaml or the app.template before adding it
    from regscale.core.app.application import Application

    app = Application()
    from regscale.core.app.utils.regscale_utils import update_regscale_config

    if param in app.config or param in app.template:
        # check the datatype provided vs what is expected
        if isinstance(val, (type(app.config[param]), type(app.template.get(param)))):
            # update init file from login
            result_msg = update_regscale_config(param, val, app=app)
            # print the result
            logger.info(result_msg)
        else:
            # try to convert val entry to an int
            try:
                int_val = int(val)
                # update init file from login
                result_msg = update_regscale_config(param, int_val, app=app)
                # print the result
                logger.info(result_msg)
            except ValueError:
                logger.error(
                    "%s needs a %s value, but a %s was provided.",
                    param,
                    type(app.template[param]),
                    type(val),
                )
                sys.exit(1)
    else:
        message = f"{param} is not required for RegScale CLI and was not added to init.yaml."
        message += "If you believe this is incorrect, please add the key and value to init.yaml manually."
        logger.error(message)


# Log into RegScale to get a token
@cli.command(name="validate_token")
def validate_token():
    """Check to see if token is valid."""
    from regscale.core.app.application import Application

    app = Application()
    if lg.is_valid(app=app):
        logger.info("RegScale token is valid.")
        sys.exit(0)
    else:
        logger.warning("RegScale token is invalid, please login.")
        sys.exit(1)


@cli.command()
@click.option(
    "--username",
    hide_input=False,
    help="RegScale User Name.",
    type=click.STRING,
    default=os.getenv("REGSCALE_USER"),
    cls=NotRequiredIf,
    not_required_if=["token"],
)
@click.option(
    "--password",
    hide_input=True,
    help="RegScale password.",
    default=os.getenv("REGSCALE_PASSWORD"),
    cls=NotRequiredIf,
    not_required_if=["token"],
)
@click.option(
    "--token",
    hide_input=True,
    help="RegScale JWT Token.",
    prompt=False,
    default=None,
    type=click.STRING,
    cls=NotRequiredIf,
    not_required_if=["username", "password", "mfa_token"],
)
@click.option(
    "--domain",
    hide_input=True,
    help="RegScale Domain (e.g. https://regscale.yourcompany.com)",
    prompt=False,
    required=False,
    default=os.getenv("REGSCALE_DOMAIN"),
    type=click.STRING,
)
@click.option(
    "--mfa_token",
    hide_input=True,
    help="RegScale MFA Token.",
    type=click.STRING,
    cls=NotRequiredIf,
    not_required_if=["token"],
)
def login(
    username: Optional[str],
    password: Optional[str],
    token: Optional[str] = None,
    domain: Optional[str] = None,
    mfa_token: Optional[str] = None,
):
    """Logs the user into their RegScale instance."""
    from regscale.core.app.application import Application

    app = Application()
    if token:
        lg.login(token=token, host=domain, app=app)
        sys.exit(0)
    if not username:
        username = click.prompt("Username", type=str)
    if not password:
        password = click.prompt("Password", type=str, hide_input=True)
    if mfa_token:
        lg.login(
            str_user=username,
            str_password=password,
            mfa_token=mfa_token,
            app=app,
            host=domain,
        )
    else:
        lg.login(str_user=username, str_password=password, app=app, host=domain)


# Check the health of the RegScale Application
@cli.command()
def healthcheck():
    """Monitoring tool to check the health of the RegScale instance."""
    hc.status()


@cli.command()
@click.option(
    "--domain",
    type=click.STRING,
    help="RegScale domain URL to skip domain prompt.",
    prompt=False,
    default=os.getenv("REGSCALE_DOMAIN"),
    required=False,
)
@click.option(
    "--username",
    type=click.STRING,
    help="RegScale User Name to skip login prompt.",
    hide_input=False,
    prompt=False,
    required=False,
    default=os.getenv("REGSCALE_USER"),
)
@click.option(
    "--password",
    type=click.STRING,
    help="RegScale password to skip login prompt.",
    hide_input=True,
    default=os.getenv("REGSCALE_PASSWORD"),
    prompt=False,
    required=False,
)
@click.option(
    "--mfa_token",
    type=click.STRING,
    help="MFA Token used to log into RegScale.",
    default="",
    prompt=False,
    required=False,
)
@click.option(
    "--user_id",
    type=click.STRING,
    help="RegScale User ID to skip login prompt.",
    hide_input=False,
    prompt=False,
    required=False,
    default=os.getenv("REGSCALE_USER_ID"),
)
@click.option(
    "--token",
    type=click.STRING,
    help="RegScale JWT Token to skip login prompt.",
    hide_input=True,
    prompt=False,
    required=False,
    default=os.getenv("REGSCALE_TOKEN"),
)
@click.option(
    "--skip-prompts",
    is_flag=True,
    help="Skip domain and login prompts.",
)
def init(
    domain: str = None,
    username: str = None,
    password: str = None,
    user_id: str = None,
    token: str = None,
    mfa_token: Optional[str] = "",
    skip_prompts: Optional[bool] = False,
):
    """Initialize RegScale CLI environment"""
    console = Console()
    from regscale.core.app.application import Application

    app = Application()
    console.print("Initializing your RegScale CLI environment...")
    # skip prompts when no-prompts flag sent
    if skip_prompts:
        os.remove("init.yaml")
        Application()
        domain_to_use = domain or os.getenv("REGSCALE_DOMAIN")
        if not domain_to_use:
            console.print("[red]You must pass a domain or set the REGSCALE_DOMAIN environment variable")
            sys.exit(1)
        app.config["domain"] = domain_to_use
        if user_id:
            app.config["userId"] = user_id
        if token:
            app.config["token"] = token
        app.save_config(conf=app.config)
        banner()
        about_display()
        console.print(f'Successfully initialized with Domain [green]{app.config["domain"]}.')
        console.print("logging in . . .")
        lg.login(token=token, host=domain_to_use, app=app)
        console.print("Logged in successfully.")
        return None

    domain_prompt = "n"
    # see if user used the --domain flag
    if not domain:
        domain_prompt = (
            input(f"Would you like to change your RegScale domain from {app.config['domain']}? (Y/n): ") or "y"
        )

    # if the user used --domain or entered y to change their domain when prompted
    if domain or domain_prompt[0].lower() == "y":
        # make sure --domain wasn't used & input yes to change their domain
        if not skip_prompts and not domain and domain_prompt[0].lower() == "y":
            # prompt user for the new domain
            domain = input("\nPlease enter your RegScale domain.\nExample: https://mydomain.regscale.com/\nDomain: ")

        # parse the domain entry for a URL
        result = urlparse(domain)

        # check if the domain provided is a valid URL
        if all([result.scheme, result.netloc]):
            from regscale.core.app.utils.regscale_utils import update_regscale_config

            # update the domain in init.yaml with the user's provided domain
            update_regscale_config(str_param="domain", val=domain, app=app)
            logger.info("Valid URL provided, init.yaml has been updated.")
        else:
            logger.error("Invalid URL provided, init.yaml was not updated.")
    # make sure --username and --password weren't used before asking if user wants to log in
    login_prompt = "n"
    if not username and not password:
        # prompt the user if they would like to log in to their RegScale instance
        login_prompt = input("Would you like to log in to your RegScale instance? (Y/n): ") or "y"
    # see if user used --username, --password or entered yes to log in to RegScale
    if username or password or login_prompt[0].lower() == "y":
        # if no username was provided, ask for one
        if not username:
            username = input("Please enter your username: ")
        # if no password was provided, ask for one
        if not password:
            # hide the password entry with getpass()
            password = getpass("Please enter your password: ")
        # try to log in with provided username and password
        lg.login(username, password, host=domain, app=app, mfa_token=mfa_token)
    banner()
    about_display()


@cli.command(name="upload_file")
@regscale_id()
@regscale_module()
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True),
    help="The path to the file to upload to RegScale.",
    prompt="File to upload to RegScale.",
    required=True,
)
def upload_file(regscale_id, regscale_module, file_path):  # noqa
    """Upload a file from your local machine to a record in RegScale."""
    file_upload(regscale_id, regscale_module, file_path)


@cli.command(name="env_info")
def env_info():
    """
    Display information about the current working environment.
    """
    import platform
    import subprocess

    import psutil

    # check if the file system is case-sensitive
    case_sensitive = False
    with open("tempfile.txt", "w") as f:
        f.write("test")
    try:
        with open("TempFile.txt", "x") as f:
            f.write("test")
        case_sensitive = True
    except FileExistsError:
        case_sensitive = False
    finally:
        os.remove("tempfile.txt")
        if case_sensitive:
            os.remove("TempFile.txt")

    from regscale.core.app.utils.app_utils import detect_shell

    shell = detect_shell() or "Unable to determine"

    # determine pip version
    try:
        result = subprocess.run(["pip", "--version"], capture_output=True, text=True, check=True)
        pip_version = result.stdout.strip()
    except subprocess.SubprocessError:
        pip_version = "Pip version not available"
    user_name = None
    print(f"Operating System: {platform.system()} {platform.release()}")
    if "linux" in platform.system().lower():
        import distro

        print(f"Distribution: {distro.name()} {distro.version()}")
        import grp
        import pwd

        user_name = pwd.getpwuid(os.getuid()).pw_name
        user_id = pwd.getpwuid(os.getuid()).pw_uid
        group_id = grp.getgrgid(user_id).gr_gid
        group = grp.getgrgid(group_id).gr_name
    elif "darwin" in platform.system().lower():
        import grp
        import pwd

        user_name = pwd.getpwuid(os.getuid()).pw_name
        user_id = pwd.getpwuid(os.getuid()).pw_uid
        group_id = os.getgid()
        group = grp.getgrgid(group_id).gr_name
    elif "windows" in platform.system().lower():
        group = "Not applicable on Windows"
        user_id = group
        group_id = group
    else:
        group = "Unable to determine on this OS"
        user_id = group
        group_id = group
    print(f"Version: {platform.version()}")
    print(f"Total Available Ram: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    print(f"Terminal: {os.getenv('TERM')}")
    print(f"Shell: {shell}")
    print(f"Python Version: {sys.version}")
    print(f"Pip Version: {pip_version}")
    print(f"RegScale CLI Version: {__version__}")
    print(f"Running in a virtual environment: {sys.prefix != sys.base_prefix}")
    print(f"Read & Write Permissions: {os.access('.', os.R_OK) and os.access('.', os.W_OK)}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Username: {user_name if user_name else os.getlogin()}")
    print(f"User's Group: {group}")
    print(f"User's ID: {user_id}")
    print(f"User's Group ID: {group_id}")
    print(f"File System Case Sensitive: {case_sensitive}")
    print(f"Running in an official RegScale container: {os.getenv('REGSCALE_CONTAINER', 'No')}")


############################################################
# Add Application Integrations
############################################################
cli.add_command(actions)  # add Reminder Functionality
cli.add_command(assessments)  # add Assessments Editor Feature
cli.add_command(catalog)  # add Catalog Management Feature
cli.add_command(compare)  # add Comparison support
cli.add_command(control_editor)  # add Control Editor Feature
cli.add_command(evidence)  # add Evidence Feature
cli.add_command(migrations)  # add data migration support
cli.add_command(issues)  # add POAM(Issues) Editor Feature
cli.add_command(model)  # add POAM(Issues) Editor Feature
cli.add_command(set_permissions)  # add builk editor for record permissions

############################################################
# Add Commercial Integrations
############################################################
cli.add_command(ad)  # add Azure Active Directory (AD) support
cli.add_command(aqua)  # Add Aqua ECR support
cli.add_command(awsv2)  # add AWS support
cli.add_command(azure)  # add Azure Integration
cli.add_command(burp)  # add Burp File Integration
cli.add_command(edr)  # add Edr connector
cli.add_command(assets)  # add Assets connector
cli.add_command(vulnerabilities)  # add Vulnerabilities connector
cli.add_command(ticketing)  # add Ticketing connector
cli.add_command(crowdstrike)  # add CrowdStrike support
cli.add_command(defender)  # add Microsoft Defender Functionality
cli.add_command(dependabot)  # add Dependabot Integration
cli.add_command(durosuite)  # add DuroSuite Integration
cli.add_command(ecr)  # add ECR Flat File Integration
cli.add_command(gcp)  # add GCP Integration
cli.add_command(gitlab)  # add GitLab
cli.add_command(grype)  # add Grype support
cli.add_command(ibm)  # add IBM AppScan support
cli.add_command(import_all)  # add import_all support
cli.add_command(jira)  # add JIRA support
cli.add_command(nexpose)  # add Nexpose support
cli.add_command(fortify)  # add NS2 support
cli.add_command(okta)  # add Okta Support
cli.add_command(prisma)  # add Prisma support
cli.add_command(qualys)  # add Qualys Functionality
cli.add_command(salesforce)  # add Salesforce support
cli.add_command(sap)  # add SAP Concur support
cli.add_command(servicenow)  # add ServiceNow support
cli.add_command(sicura)  # add Sicura Integration
cli.add_command(snyk)  # add Snyk support
cli.add_command(veracode)  # add Veracode Integration
cli.add_command(sonarcloud)  # add SonarCloud Integration
cli.add_command(stig)  # add STIGv2 support
cli.add_command(stig_mapper)  # add STIG Mapper support
cli.add_command(tenable)  # add Tenable & TenableV2 support
cli.add_command(trivy)  # add Trivy support
cli.add_command(wiz)  # add Wiz support
cli.add_command(xray)  # add JFrog Xray support

############################################################
# Add Public Integrations
############################################################
cli.add_command(alienvault)  # add Alienvault OTX integration
cli.add_command(cisa)  # add CISA support
cli.add_command(csam)  # add CSAM support
cli.add_command(emass)  # add eMASS support
cli.add_command(fedramp)  # add FedRAMP support
cli.add_command(nist)  # add Nist_Catalog support
cli.add_command(oscal)  # add OSCAL support
cli.add_command(criticality_updater)  # add Criticality Updater support

# start function for the CLI
if __name__ == "__main__":
    cli()
