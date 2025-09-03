"""Task for parallelization testing which sleeps a configurable amount of time"""

from time import sleep

from dkist_processing_core import TaskBase

__all__ = ["WaitTask"]


SLEEP_TIME = 60


class WaitTask(TaskBase):
    def run(self) -> None:
        sleep(SLEEP_TIME)
