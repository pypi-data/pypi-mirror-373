"""Generate a REST API from the click model."""

from typing import List, Union
from io import StringIO
from contextlib import redirect_stdout

try:
    from flask import Flask, request
except ImportError:
    raise ImportError("regscale must be installed with the [server] extra.")

from regscale.models.click_models import ClickGroup, ClickCommand, ClickOption
from regscale.core.utils.click_utils import REGSCALE_CLI


app = Flask(__name__)


def generate_routes(group: ClickGroup, path: str = ""):
    """Generate routes recursively
    :param ClickGroup group: a ClickGroup BaseModel
    :param str path: the endpoint path
    """
    for command in group.commands:
        if isinstance(command, ClickCommand):
            endpoint_path = f"{path}/{command.name}"

            # create the view function
            def create_view_func(command_: ClickCommand):
                def view_func():
                    params = {param.name: request.json.get(param.name) for param in command_.params}
                    output_stream = StringIO()
                    with redirect_stdout(output_stream):
                        command_.callback(**params)
                        output = output_stream.getvalue()
                    return {"input": f"regscale {command_.name}", "output": output}

                return view_func

            # replace / with _ to create a unique command name
            unique_command_name = endpoint_path.replace("/", "__")
            # determine methods
            methods = ["POST"] if command.params else ["GET"]

            # add the route to the Flask app
            app.add_url_rule(
                rule=endpoint_path,
                endpoint=unique_command_name,
                view_func=create_view_func(command),
                methods=methods,
            )
        elif isinstance(command, ClickGroup):
            generate_routes(command, f"{path}/{command.name}")


generate_routes(REGSCALE_CLI)


def run_app(port: int = 5555, debug: bool = False):
    """Run the CLI as a flask app
    :param int port: the port to serve flask on
    :param bool debug: should it be run in debug mode
    """
    app.run(port=port, debug=debug)
