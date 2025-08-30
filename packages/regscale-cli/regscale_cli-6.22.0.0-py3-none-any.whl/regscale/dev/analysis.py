"""Provide analysis functions for regscale."""

import ast
import itertools
import math
import os

import git
import matplotlib.pyplot as plt
from radon.complexity import cc_visit
from radon.metrics import h_visit
from radon.raw import analyze

from regscale.core.app.logz import create_logger

INIT_FILE = "__init__.py"


def find_py_files(root_folder: str) -> list[str]:
    """Find all Python files in a given root folder and its subdirectories

    :param str root_folder: the root folder to search
    :return: a list of Python files
    :rtype: list[str]
    """
    py_files = []
    for root, dirs, files in os.walk(root_folder):
        py_files.extend([os.path.join(root, f) for f in files if f.endswith(".py")])
    return py_files


def analyze_git(folder_path: str = ".", subfolder: str = "regscale") -> dict:
    """Analyze a git repository at the repo_path

    :param str folder_path: the path to the folder to analyze
    :param str subfolder: the subfolder to analyze
    :return: a dictionary of git information
    :rtype: dict
    """
    log = create_logger()
    try:
        # initialize a git repository object
        repo = git.Repo(folder_path)
    except git.InvalidGitRepositoryError:
        log.error(f"{folder_path} is not a valid git repository")
        return {}
    # initialize the metrics dictionary
    git_metrics = {}
    full_subfolder_path = os.path.join(folder_path, subfolder)
    py_files = find_py_files(full_subfolder_path)
    for py_file in py_files:
        if INIT_FILE in py_file:
            continue
        commit_count = 0
        contributors = set()
        file_path_in_repo = os.path.relpath(py_file, folder_path)
        for commit in repo.iter_commits(paths=file_path_in_repo):
            commit_count += 1
            contributors.add(commit.author.name)
        file_metrics = {
            "commit_count": commit_count,
            "contributors": list(contributors),
            "num_contributors": len(contributors),
            "lines": len(open(py_file).readlines()),
            "path": file_path_in_repo,
        }
        # get the date of the last update for this file
        last_commit = next(repo.iter_commits(paths=file_path_in_repo), None)
        file_metrics["last_update_date"] = (
            last_commit.committed_datetime.strftime("%Y-%m-%d %H:%M") if last_commit else None
        )
        git_metrics[py_file[2:]] = file_metrics
    return git_metrics


def parse_comments(file_path: str) -> int:
    """Parse the number of comments in a given file

    :param str file_path: the path to the file to parse
    :return: the number of comments
    :rtype: int
    """
    comments = 0
    with open(file_path, "r") as f:
        for line in f:
            if line.strip().startswith("#"):
                comments += 1
                continue
            if '"""' in line or "'''" in line:
                comments += 0.5
            elif "# " in line or "  #" in line:
                comments += 1
    return comments


def parse_code(file_path: str) -> dict:
    """Parse a python file and return a dictionary of the parsed code metrics

    :param str file_path: the path to the file to parse
    :return: a dictionary of the parsed code metrics
    :rtype: dict
    """
    comments = parse_comments(file_path)
    # set the metrics
    metrics = {
        "Assignments": 0,
        "Comments": comments,
        "Conditionals": 0,
        "Classes": 0,
        "Functions": 0,
        "Imports": 0,
        "Loops": 0,
        "Statements": 0,
    }
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)
    # Generate the AST
    # Walk through all nodes in the AST
    for node in ast.walk(tree):
        if isinstance(node, ast.stmt):
            metrics["Statements"] += 1
        if isinstance(node, ast.FunctionDef):
            metrics["Functions"] += 1
        elif isinstance(node, ast.Assign):
            metrics["Assignments"] += 1
        elif isinstance(node, ast.ClassDef):
            metrics["Classes"] += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            metrics["Imports"] += 1
        elif isinstance(node, (ast.While, ast.For)):
            metrics["Loops"] += 1
        elif isinstance(node, ast.If):
            metrics["Conditionals"] += 1
    metrics["Statements"] -= metrics["Imports"]  # imports are statements too
    return metrics


def find_global_variables(file_path: str) -> dict:
    """Find all global variables in a given python file

    :param str file_path: the path to the file to analyze
    :return: a list of global variables
    :rtype: dict
    """
    with open(file_path, "r") as f:
        code = f.read()
    # Generate the AST
    tree = ast.parse(code)
    global_variables = []
    num_globals = 0
    # Walk through all nodes in the AST
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            global_variables.extend(target.id for target in node.targets if isinstance(target, ast.Name))
            num_globals += 1
    return {"Global Variables": global_variables, "Num Globals": num_globals}


def analyze_code_smells(
    file_path: str,
    long_method_threshold: int = 20,
    param_threshold: int = 4,
    nested_loop_threshold: int = 3,
) -> dict:
    """Analyze code smells for a given python file

    :param str file_path: the path to the file to analyze
    :param int long_method_threshold: the threshold for a long method
    :param int param_threshold: the threshold for a long parameter list
    :param int nested_loop_threshold: the threshold for nested loops
    :return: a dictionary of code smells
    :rtype: dict
    """
    long_methods = []
    many_param_methods = []
    nested_loops = []
    global_vars = []
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # find long methods
            line_count = node.end_lineno - node.lineno + 1
            if line_count > long_method_threshold:
                long_methods.append(node.name)
            # too many parameters
            if len(node.args.args) > param_threshold:
                many_param_methods.append({"name": node.name, "param_count": len(node.args.args)})
        # nested loops
        elif isinstance(node, (ast.For, ast.While)):
            nested_count = sum(isinstance(_, (ast.For, ast.While)) for _ in ast.walk(node))
            if nested_count > nested_loop_threshold:
                nested_loops.append({"lineno": node.lineno, "nested_count": nested_count})
        # find global variables
        elif isinstance(node, ast.Global):
            global_vars.extend(node.names)
    return {
        "Long Methods": long_methods,
        "Many param Methods": many_param_methods,
        "Nested Loops": nested_loops,
        "Global Vars": global_vars,
        "Num Long Methods": len(long_methods),
        "Num Many Param Methods": len(many_param_methods),
        "Num Nested Loops": len(nested_loops),
        "Num Global Vars": len(global_vars),
    }


def analyze_code_files(root_folder: str = "regscale") -> dict:
    """Analyze all Python files in a given root folder and its subdirectories

    :param str root_folder: the root folder to search
    :return: a dictionary of code metrics
    :rtype: dict
    """
    py_files = find_py_files(root_folder)
    return {
        file_path: parse_code(file_path)
        | analyze_text_search(file_path)
        | analyze_complexity_metrics(file_path)
        | find_global_variables(file_path)
        | analyze_fan_metrics(file_path)
        | analyze_code_smells(file_path)
        for file_path in py_files
        if INIT_FILE not in file_path
    }


def analyze_text_search(file_path: str) -> dict:
    """Search for FIXMEs and TODOs in a given python file

    :param str file_path: the path to the file to search
    :return: a dictionary of FIXMEs and TODOs
    :rtype: dict
    """
    metrics = {
        "FIXMEs": 0,
        "TODOs": 0,
        "TODO Density": 0.0,
        "FIXME Density": 0.0,
    }
    with open(file_path, "r") as f:
        lines = len(f.readlines())
        f.seek(0)
        for line in f:
            if "# FIXME" in line.upper():
                metrics["FIXMEs"] += 1
            if "# TODO" in line.upper():
                metrics["TODOs"] += 1
    metrics["FIXME Density"] = metrics["FIXMEs"] / lines if lines else 0.0
    metrics["TODO Density"] = metrics["TODOs"] / lines if lines else 0.0
    return metrics


def analyze_complexity_metrics(file_path: str) -> dict:
    """Analyze the complexity metrics for a given python file

    :param str file_path: the path to the file to analyze
    :return: a dictionary of complexity metrics
    :rtype: dict
    """
    with open(file_path, "r") as f:
        code = f.read()
    # Radon metrics
    raw_metrics = analyze(code)
    halstead_metrics = h_visit(code)
    cyclomatic_metrics = cc_visit(code)
    complexity = sum((complexity_.complexity for complexity_ in cyclomatic_metrics))
    return {
        "Lines of Code": raw_metrics.loc,
        "Lines of Comments": raw_metrics.comments,
        "Maintainability Index": calculate_maintainability_index(
            volume=halstead_metrics.total.volume,
            complexity=complexity,
            loc=raw_metrics.loc,
        ),
        "Halstead Vocabulary": halstead_metrics.total.vocabulary,
        "Halstead Difficulty": halstead_metrics.total.difficulty,
        "Halstead Effort": halstead_metrics.total.effort,
        "Halstead Volume": halstead_metrics.total.volume,
        "Cyclomatic Complexity": complexity,
        "Complexity/LOC Ratio": (complexity / raw_metrics.loc if raw_metrics.loc else 0.0),
    }


def calculate_maintainability_index(volume: float, complexity: float, loc: int) -> float:
    """Calculate the maintainability index
    MI = 171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code)

    :param float volume: the Halstead Volume
    :param float complexity: the Cyclomatic Complexity
    :param int loc: the Lines of Code
    :return: the maintainability index
    :rtype: float
    """
    try:
        return 171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(loc)
    except ValueError:
        return 0.0


def analyze_fan_metrics(file_path: str) -> dict:
    """Analyze Fan-in and Fan-out metrics for each function in a Python file

    :param str file_path: the path to the file to analyze
    :return: a dictionary of Fan-in and Fan-out metrics
    :rtype: dict
    """
    fan_in = {}
    fan_out = {}
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            fan_out[node.name] = 0
            for sub_node in ast.walk(node):
                if isinstance(sub_node, ast.Call) and isinstance(sub_node.func, ast.Name):
                    fan_out[node.name] += 1
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id
            fan_in[func_name] = fan_in.get(func_name, 0) + 1
    return {
        "Fan In": fan_in,
        "Fan Out": fan_out,
        "Num Fan In": len(fan_in),
        "Num Fan Out": len(fan_out),
    }


def generate_heatmap(
    data: dict,
    metric: str,
    figsize: tuple = (50, 50),
    font_size: int = 7,
    show: bool = False,
) -> plt.Figure:
    """Generate a heatmap of the given metric

    :param dict data: the data to plot
    :param str metric: the metric to plot
    :param tuple figsize: the figure size
    :param int font_size: the font size
    :param bool show: whether to show the plot
    :return: matplotlib.pyplot.Figure
    :rtype: plt.Figure
    """
    import numpy as np  # Optimize import performance

    # Collect file names and their corresponding metric values
    file_names = list(data.keys())
    values = [item.get(metric, 0) for item in data.values()]

    # Calculate grid dimensions based on the number of files
    grid_size = int(np.ceil(np.sqrt(len(file_names))))

    # Create an empty grid
    grid = np.zeros((grid_size, grid_size))

    # Fill in the grid with metric values
    for i, j in itertools.product(range(grid_size), range(grid_size)):
        index = i * grid_size + j
        if index < len(values):
            grid[i, j] = values[index]

    # Generate the heatmap with increased figure size
    fig, ax = plt.subplots(figsize=figsize)
    cax = ax.matshow(grid, cmap="coolwarm")
    colorbar = fig.colorbar(cax)
    colorbar.ax.tick_params(labelsize=40)

    # Remove tick marks
    ax.set_xticks([])
    ax.set_yticks([])

    # Label the squares with file names, adjusting font size for readability
    for i, j in itertools.product(range(grid_size), range(grid_size)):
        index = i * grid_size + j
        if index < len(file_names):
            file_name = str(file_names[index])
            metric_value = "{:.2f}".format(values[index]) if "." in str(values[index]) else str(values[index])
            plt.text(
                j,
                i,
                f"{file_name}\n{metric_value}",
                va="center",
                ha="center",
                fontsize=font_size,
                wrap=True,
            )
    plt.title(metric, fontsize=70)
    if show:
        plt.show()
    return plt.gcf()


def generate_barplot(
    data: dict,
    metric: str,
    top_n: int = 20,
    figsize: tuple = (50, 50),
    show: bool = False,
) -> plt.Figure:
    """Generate a barplot of the given metric

    :param dict data: the data to plot
    :param str metric: the metric to plot
    :param int top_n: the number of top items to plot
    :param tuple figsize: the figure size
    :param bool show: whether to show the plot
    :return: matplotlib.pyplot.Figure
    :rtype: plt.Figure
    """
    values = {file: item.get(metric, 0) for file, item in data.items() if not file.endswith(INIT_FILE)}
    if metric == "Maintainability Index":
        # sort by the lowest values for Maintainability Index
        filtered_values = {file: value for file, value in values.items() if int(value) != 0}
        # also filter out any files with a Maintainability Index of 0
        sorted_values = dict(sorted(filtered_values.items(), key=lambda item: item[1])[:top_n])
    else:
        # sort by the highest values for all other metrics
        sorted_values = dict(sorted(values.items(), key=lambda item: item[1], reverse=True)[:top_n])
    _, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(sorted_values.keys(), sorted_values.values())
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            str(round(height, 2)),
            va="bottom",
            ha="center",
            fontsize=30,
        )
    plt.xticks(rotation=90, ha="right", fontsize=22)
    plt.yticks(fontsize=40)
    plt.title(f"Top 20 {metric}", fontsize=70)
    plt.xlabel("File", fontsize=40)
    plt.ylabel(metric, fontsize=40)
    if show:
        plt.show()
    return plt.gcf()


def combine_git_and_code_metrics() -> dict:
    """Combine the git and code metrics
    :return: a dictionary of combined git and code metrics
    :rtype: dict
    """
    git_metrics = analyze_git()
    code_metrics = analyze_code_files()
    return {
        key: {**git_metrics.get(key, {}), **code_metrics.get(key, {})} for key in set(git_metrics) | set(code_metrics)
    }
