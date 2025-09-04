import typing as t
from pathlib import Path

import yaml

from meili_sdk.schedules.exceptions import TaskFileDoesNotExist
from meili_sdk.schedules.models import ScheduledTask


class ScheduleLoader:
    def load(self):
        # TODO implement smach loader
        return self.load_yaml()

    def load_yaml(self):
        path = Path.home().joinpath(".meili", "tasks.yaml")
        data = self.__load_yaml(path)

        schedules = []
        for schedule in data:
            schedules.append(ScheduledTask(**schedule))
        return schedules

    @staticmethod
    def __load_yaml(path: t.Union[Path, str]):
        try:
            file = open(path, "r")
            data = yaml.safe_load(file.read())
        except FileNotFoundError:
            raise TaskFileDoesNotExist
        else:
            file.close()
            return data
