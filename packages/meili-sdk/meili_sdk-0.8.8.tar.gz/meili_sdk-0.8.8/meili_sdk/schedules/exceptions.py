from meili_sdk.exceptions import MeiliException


class TaskFileDoesNotExist(MeiliException):
    msg = "Task schedule file does not exist"
