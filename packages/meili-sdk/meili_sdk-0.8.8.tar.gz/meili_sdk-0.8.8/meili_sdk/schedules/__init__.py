from .exceptions import TaskFileDoesNotExist
from .loader import ScheduleLoader


def load_schedules():
    return ScheduleLoader().load()
