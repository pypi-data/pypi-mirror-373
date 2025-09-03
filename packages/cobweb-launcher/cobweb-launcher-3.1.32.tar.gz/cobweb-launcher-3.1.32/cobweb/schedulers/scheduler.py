import threading

from typing import Callable
from cobweb.base import TaskQueue
from abc import ABC, abstractmethod


class Scheduler(ABC, threading.Thread):

    # __LAUNCHER_FUNC__ = ["_reset", "_scheduler", "_insert", "_refresh", "_delete"]

    def __init__(
            self,
            task,
            project,
            stop: threading.Event,
            pause: threading.Event,
            task_queue: TaskQueue,
            callback_register: Callable
    ):
        super().__init__()
        self.task = task
        self.project = project
        from cobweb import setting

        self.task_model = setting.TASK_MODEL
        self.seed_reset_seconds = setting.SEED_RESET_SECONDS
        self.scheduler_wait_seconds = setting.SCHEDULER_WAIT_SECONDS
        self.new_queue_wait_seconds = setting.NEW_QUEUE_WAIT_SECONDS
        self.done_queue_wait_seconds = setting.DONE_QUEUE_WAIT_SECONDS
        self.todo_queue_full_wait_seconds = setting.TODO_QUEUE_FULL_WAIT_SECONDS
        self.before_scheduler_wait_seconds = setting.BEFORE_SCHEDULER_WAIT_SECONDS

        self.todo_queue_size = setting.TODO_QUEUE_SIZE
        self.new_queue_max_size = setting.NEW_QUEUE_MAX_SIZE
        self.done_queue_max_size = setting.DONE_QUEUE_MAX_SIZE
        self.upload_queue_max_size = setting.UPLOAD_QUEUE_MAX_SIZE

        self.stop = stop
        self.pause = pause

        self.task_queue = task_queue

        self.callback_register = callback_register

    @abstractmethod
    def reset(self):
        ...

    @abstractmethod
    def schedule(self):
        ...

    @abstractmethod
    def insert(self):
        ...

    @abstractmethod
    def refresh(self):
        ...

    @abstractmethod
    def delete(self):
        ...


