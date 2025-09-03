"""Tools and functions for the generation of documentation."""

import os
import subprocess
from typing import Optional, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from regscale.core.app.api import Api

from sphinx.application import Sphinx
from sphinx.cmd.quickstart import generate

from regscale import __version__

INDEX_RST = "index.rst"
APP_JSON = "application/json"


def init_sphinx(
    docs_path: str = "docs",
    project_name: str = "RegScale-CLI",
    project_version: str = __version__,
    project_author: str = "Travis Howerton",
) -> None:
    """Initialize Sphinx for generating documentation

    :param str docs_path: Path to the docs folder
    :param str project_name: Name of the project
    :param str project_version: Version of the project
    :param str project_author: Author of the project
    :rtype: None
    """
    generate(
        {
            "path": docs_path,
            "sep": False,
            "dot": "_",
            "project": project_name,
            "name": project_name,
            "author": project_author,
            "version": project_version,
            "release": project_version,
            "suffix": ".rst",
            "ext_autodoc": True,
            "ext_doctest": False,  # change to true later?
            "ext_intersphinx": False,  # change to true later?
            "ext_todo": False,  # change to true later?
            "ext_coverage": False,  # change to true later?
            "ext_mathjax": False,  # change to true later?
            "ext_ifconfig": False,  # change to true later?
            "ext_viewcode": False,  # change to true later?
            "makefile": True,
            "batchfile": False,
            "make_mode": False,
            "quiet": True,
            "master": "index",
            "root_doc": "index",
        }
    )


def enable_extensions_in_conf(docs_path: str, hide_source: bool = False) -> None:
    """Enable extensions in the conf.py file

    :param str docs_path: Path to the docs folder
    :param bool hide_source: Hide the source code link in the generated documentation, defaults to False
    :rtype: None
    """
    conf_file_path = os.path.join(docs_path, "conf.py")
    with open(conf_file_path, "r+") as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if line.startswith("extensions = []"):
                f.write("extensions = [\n")
                f.write(
                    "    'sphinx.ext.autodoc',\n"
                    "    'sphinx.ext.napoleon',\n"
                    "    'sphinx.ext.autosectionlabel',\n"
                    "    'sphinx.ext.autodoc.typehints',\n"
                    "    'sphinx.ext.coverage',\n"
                    "    'sphinx_click',\n"
                )
                if not hide_source:
                    f.write("    'sphinx.ext.viewcode',\n")
                f.write("]\n")
            elif line.startswith("html_theme"):
                f.write("html_theme = 'classic'\ntodo_include_todos = True\n")
            else:
                f.write(line)
        f.truncate()


def create_master_index_rst(docs_path: str, src_path: str, title: str = "RegScale-CLI Documentation") -> None:
    """Create the master index.rst file

    :param str docs_path: Path to the docs folder
    :param str src_path: Path to the source folder
    :param str title: Title of the documentation, defaults to "RegScale-CLI Documentation"
    :rtype: None
    """
    with open(os.path.join(docs_path, INDEX_RST), "w") as f:
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 2\n\n")
        f.write("    click_commands\n")
        f.write("    regscale_regscale\n")
        for item in os.listdir(src_path):
            if os.path.isdir(os.path.join(src_path, item)) and item not in [
                "__pycache__",
                "__init__.py",
            ]:
                f.write(f"   {item}/index\n")
        for item in os.listdir(docs_path):
            if item.endswith(".rst") and item != INDEX_RST:
                module_name = os.path.splitext(item)[0]
                f.write(f"   {module_name}\n")


def create_click_commands_rst(docs_path: str) -> None:
    """Create .rst file for the click commands

    :param str docs_path: Path to the docs folder
    :rtype: None
    """
    # this format cannot be altered because it will break the Sphinx build
    content = """
RegScale-CLI Click Commands
===========================

.. click:: regscale.regscale:cli
    :prog: regscale
    :show-nested:

.. click:: regscale.dev.cli:cli
    :prog: regscale-dev
    :show-nested:

"""
    with open(os.path.join(docs_path, "click_commands.rst"), "w") as f:
        f.write(content)


def create_rst_for_module(module_name: str, rst_path: str) -> None:
    """Create .rst file for a Python module

    :param str module_name: Name of the module
    :param str rst_path: Path to the .rst file
    :rtype: None
    """
    # this format cannot be altered because it will break the Sphinx build
    content = f"""
{module_name}
{'=' * len(module_name)}

.. automodule:: {module_name.replace(',', '_')}
    :members:
    :undoc-members:
    :show-inheritance:
"""
    with open(os.path.join(rst_path, f"{module_name.replace('.', '_')}.rst"), "w") as f:
        f.write(content)


def traverse_and_create_rst(
    root_path: str,
    current_path: str,
    rst_path: str,
    prefix: str = "",
    exclude_dirs: Optional[list[str]] = None,
) -> None:
    """
    Traverse through the directory recursively and create .rst files for each Python module

    :param str root_path: Root path of the project
    :param str current_path: Current path of the directory
    :param str rst_path: Path to the .rst file(s)
    :param str prefix: Prefix to be added to the module name, defaults to ""
    :param Optional[list[str]] exclude_dirs: List of directories to exclude, defaults to ["__pycache__"]
    :rtype: None
    """
    # Check if the directory has any subdirectories with Python files
    if exclude_dirs is None:
        exclude_dirs = ["__pycache__"]
    has_subdir_with_py = any(
        os.path.isdir(os.path.join(current_path, item))
        and any(sub_item.endswith(".py") for sub_item in os.listdir(os.path.join(current_path, item)))
        for item in os.listdir(current_path)
        if item not in exclude_dirs
    )

    for item in os.listdir(current_path):
        if item in exclude_dirs:
            continue
        item_path = os.path.join(current_path, item)
        if os.path.isdir(item_path):
            new_rst_path = os.path.join(rst_path, item)
            os.makedirs(new_rst_path, exist_ok=True)
            new_prefix = f"{prefix}.{item}" if prefix else item

            # Recur further only if this directory has subdirectories with Python files
            if has_subdir_with_py:
                traverse_and_create_rst(root_path, item_path, new_rst_path, new_prefix, exclude_dirs)

            # Generate index.rst for this sub-directory
            with open(os.path.join(new_rst_path, "index.rst"), "w") as f:
                f.write(f"{item}\n")
                f.write("=" * len(item) + "\n\n")
                f.write(".. toctree::\n    :maxdepth: 1\n\n")
                for sub_item in os.listdir(new_rst_path):
                    if sub_item.endswith(".rst"):
                        module_name = os.path.splitext(sub_item)[0]
                        f.write(f"    {module_name}\n")
                    elif os.path.isdir(os.path.join(new_rst_path, sub_item)):
                        f.write(f"    {sub_item}/index\n")
        elif item.endswith(".py") and item != "__init__.py":
            # Generate RST only if this directory does not have subdirectories with Python files
            if not has_subdir_with_py:
                module_name = f"{prefix}.{os.path.splitext(item)[0]}" if prefix else os.path.splitext(item)[0]
                create_rst_for_module(module_name, rst_path)


def build_docs(src_path: str, build_path: str, doctype: str) -> None:
    """Build the documentation

    :param str src_path: Path to the source folder
    :param str build_path: Path to the build folder
    :param str doctype: Type of documentation
    :rtype: None
    """
    app = Sphinx(src_path, src_path, build_path, build_path, doctype)
    app.build()


def generate_docs(
    project_path: str = os.getcwd(),
    src_folder_name: str = "regscale",
    docs_folder_name: str = "docs",
    hide_source: bool = False,
) -> None:
    """Generate the documentation

    :param str project_path: Path to the project, defaults to os.getcwd()
    :param str src_folder_name: Name of the source folder, defaults to "regscale"
    :param str docs_folder_name: Name of the docs folder, defaults to "docs"
    :param bool hide_source: Hide the source code in the documentation, defaults to False
    :rtype: None
    """
    docs_path = os.path.join(project_path, docs_folder_name)
    src_path = os.path.join(project_path, src_folder_name)
    exclude_dirs = None
    os.makedirs(docs_path, exist_ok=True)
    init_sphinx(docs_path)
    enable_extensions_in_conf(docs_path="docs", hide_source=hide_source)
    create_click_commands_rst(docs_path)
    create_master_index_rst(docs_path, src_path)
    # traverse through the regscale directory recursively to create .rst files
    if hide_source:
        exclude_dirs = ["dev", "airflow", "ansible", "regscale-dev", "__pycache__", "docs"]
    traverse_and_create_rst(
        root_path=src_path, current_path=src_path, rst_path=docs_path, prefix=src_folder_name, exclude_dirs=exclude_dirs
    )
    # build the documentation
    build_path = os.path.join(docs_path, "_build")
    build_docs(docs_path, build_path, "html")
    # build_docs(docs_path, build_path, 'text')
    subprocess.run([f"sphinx-apidoc -o {docs_path} {src_path}"], shell=True)


def update_readme_io(api: "Api", root: str, file: str) -> None:
    """
    Update the readme.io documentation for the CLI

    :param Api api: The API object to use to update the documentation
    :param str root: The root directory of containing file with readme io slug and data
    :param str file: File name to parse the readme io slug and data to update readme.io
    :rtype: None
    """
    readme_slug = None
    payload_data = ""
    with open(f"{root}/{file}", "r") as f:
        for line in f:
            if "# readme_slug:" in line:
                readme_slug = line.split(":")[1].strip()
            else:
                for payload_line in f:
                    payload_data += payload_line
    payload_data = payload_data.lstrip("\n")

    # get the current data from the readme.io project
    res = api.get(f"https://dash.readme.com/api/v1/docs/{readme_slug}")
    if res.raise_for_status() and not res.ok:
        api.logger.error(
            f"Failed to retrieve readme.io slug: {readme_slug}\n{res.status_code}: {res.reason}\n{res.text}"
        )
        current_data = {"body": "", "hidden": False}
    else:
        current_data = res.json()

    if current_data["body"] == payload_data:
        api.logger.info(f"Readme.io slug: {readme_slug} is already up to date")
        return
    api.logger.info(f"Updating readme.io slug: {readme_slug} with {root}/{file} and payload {payload_data}")
    res = api.put(
        f"https://dash.readme.com/api/v1/docs/{readme_slug}",  # This is the same url for every readme.io project
        json={"hidden": current_data["hidden"], "body": payload_data},
        headers={"Content-Type": APP_JSON},
    )
    if not res.raise_for_status() and res.ok:
        api.logger.info(f"Successfully updated readme.io slug: {readme_slug}")
    else:
        api.logger.error(f"Failed to update readme.io slug: {readme_slug}\n{res.status_code}: {res.reason}\n{res.text}")


def update_confluence(api: "Api", url: str, root: str, file: str) -> None:
    """
    Update the confluence documentation for the CLI

    :param Api api: The API object to use to update the documentation
    :param str url: The base URL for the confluence instance
    :param str root: The root directory of containing file with confluence id and data
    :param str file: File name to parse the confluence id and data from to update confluence
    :rtype: None
    """
    import json

    payload = {
        "id": None,
        "type": "page",
        "status": "current",
        "title": None,
        "version": {"number": 1},
        "body": {"storage": {"value": "", "representation": "storage"}},
    }
    headers = {"Content-Type": APP_JSON}
    confluence_id, parsed_data = _parse_confluence_md(root, file)

    # get the current version of the confluence page
    res = api.get(f"{url}/rest/api/content/{confluence_id}?expand=body.storage,version", headers=headers)
    if res.raise_for_status() or not res.ok:
        api.logger.error(f"Failed to get confluence id: {confluence_id}\n{res.status_code}: {res.reason}\n{res.text}")
        return
    json_data = res.json()
    payload["title"] = json_data["title"]
    payload["body"]["storage"]["value"] = parsed_data
    payload["version"]["number"] = json_data["version"]["number"] + 1
    api.logger.debug(f"Updated version number from {json_data['version']['number']} to {payload['version']['number']}")
    api.logger.info(f"Updating confluence id {confluence_id} with {root}/{file} and body {json_data}")
    res = api.put(
        f"{url}/rest/api/content/{confluence_id}",
        json=payload,
        headers=headers,
    )
    if not res.raise_for_status() and res.ok:
        api.logger.info(f"Successfully updated confluence id: {confluence_id}")
    else:
        api.logger.error(
            f"Failed to update confluence id: {confluence_id}\n{res.status_code}: {res.reason}\n{res.text}"
        )


def _parse_confluence_md(root: str, file: str) -> tuple[str, str]:
    """
    Parse the confluence id and data from the markdown file

    :param str root: The root directory of containing file with confluence id and data
    :param str file: File name to parse the confluence id and data from
    :rtype: tuple[str, str]
    """
    confluence_id = None
    payload = ""
    with open(f"{root}/{file}", "r") as f:
        for line in f:
            if "# ConfluenceID:" in line:
                confluence_id = line.split(":")[1].strip()
            else:
                for payload_line in f:
                    payload += payload_line
    # parse the string data between the first and last occurrence of ``` to get the payload
    payload = payload[payload.find("```html") + 7 : payload.rfind("```")]
    return confluence_id, payload
