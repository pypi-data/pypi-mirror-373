"""Provide information related to branches in python."""


def tri_branch_func(pull_from: str, negative_task: str, neutral_task: str, positive_task: str, **kwargs: dict) -> str:
    """Return the branch name

    :param str pull_from: the task_id to pull from
    :param str negative_task: the task_id to go to if the pull_from task returns -1
    :param str neutral_task: the task_id to go to if the pull_from task returns 0
    :param str positive_task: the task_id to go to if the pull_from task returns 1
    :param dict **kwargs: additional keyword arguments
    :return: the task_id to go to
    :rtype: str
    """
    ti = kwargs["ti"]
    var = ti.xcom_pull(task_ids=pull_from)
    if var == -1:
        return negative_task
    elif var == 0:
        return neutral_task
    else:
        return positive_task
