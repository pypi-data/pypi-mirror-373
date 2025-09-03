import time
import threading
from typing import Callable, Type
from cobweb.pipelines import Pipeline
from cobweb.base import TaskQueue, logger, Status
from cobweb.utils import check_pause


class Uploader(threading.Thread):

    def __init__(
            self,
            task: str,
            project: str,
            stop: threading.Event,
            pause: threading.Event,
            task_queue: TaskQueue,
            callback_register: Callable,
            SpiderPipeline: Type[Pipeline]
    ):
        super().__init__()
        self.task = task
        self.project = project

        self.stop = stop
        self.pause = pause

        self.task_queue = task_queue
        self.callback_register = callback_register

        from cobweb import setting

        self.upload_size = setting.UPLOAD_QUEUE_MAX_SIZE
        self.wait_seconds = setting.UPLOAD_QUEUE_WAIT_SECONDS

        self.pipeline = SpiderPipeline(task=self.task, project=self.project)

        logger.debug(f"Uploader instance attrs: {self.__dict__}")

    @check_pause
    def upload_data(self):
        try:
            data_info, task_ids = dict(), set()
            if task_list := self.task_queue.get_task_by_status(
                    status=Status.UPLOAD, limit=self.upload_size
            ):
                for task_item in task_list:
                    upload_data = self.pipeline.build(task_item.data)
                    data_info.setdefault(task_item.data.table, []).append(upload_data)
                    task_ids.add(task_item.task_id)

                for table, datas in data_info.items():
                    try:
                        self.pipeline.upload(table, datas)
                    except Exception as e:
                        logger.info(e)

            self.task_queue.remove(task_ids)
        except Exception as e:
            logger.info(e)

        if self.task_queue.status_length(status=Status.UPLOAD) < self.upload_size:
            time.sleep(self.wait_seconds)

    def run(self):
        self.callback_register(self.upload_data, tag="Uploader")


