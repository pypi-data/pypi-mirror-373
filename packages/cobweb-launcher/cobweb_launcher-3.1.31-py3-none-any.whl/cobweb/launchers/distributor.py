import time
import threading
import traceback

from inspect import isgenerator
from typing import Callable, Type
from urllib.parse import urlparse
from requests import Response as Res

from cobweb.crawlers import Crawler
from cobweb.utils import LoghubDot, check_pause
from cobweb.constant import DealModel, LogTemplate
from cobweb.base import Seed, Status, TaskQueue, BaseItem, Request, Response, logger


class Distributor(threading.Thread):

    def __init__(
            self,
            task: str,
            project: str,
            task_queue: TaskQueue,
            stop: threading.Event,
            pause: threading.Event,
            callback_register: Callable,
            SpiderCrawler: Type[Crawler]
    ):
        super().__init__()
        self.task = task
        self.project = project
        self.stop = stop
        self.pause = pause

        self.task_queue = task_queue

        self.callback_register = callback_register
        self.Crawler = SpiderCrawler

        from cobweb import setting
        self.time_sleep = setting.SPIDER_TIME_SLEEP
        self.thread_num = setting.SPIDER_THREAD_NUM
        self.max_retries = setting.SPIDER_MAX_RETRIES
        self.record_failed = setting.RECORD_FAILED_SPIDER
        self.loghub_dot = LoghubDot(stop=stop)  # todo

        logger.debug(f"Distribute instance attrs: {self.__dict__}")

    def distribute(self, task_id, item, _id: int):
        if isinstance(item, Request):
            item.seed.params.start_time = time.time()
            self.process(task_id=task_id, item=item, callback=self.Crawler.download, _id=1)

        elif isinstance(item, Response):
            if _id == 2:
                raise TypeError("parse function can't yield a Response instance")
            dot = isinstance(item.response, Res)
            self.spider_logging(item.seed, item, dot=dot)  # todo: update
            self.process(task_id=task_id, item=item, callback=self.Crawler.parse, _id=2)

        elif isinstance(item, BaseItem):
            self.task_queue.add_task(
                data=item,
                status=Status.UPLOAD,
                parent_id=task_id
            )

        elif isinstance(item, Seed):
            self.task_queue.add_task(
                task_id=item.sid,
                data=item,
                status=Status.INSERT,
                priority=item.params.priority,
                parent_id=task_id
            )

        elif isinstance(item, str) and item != DealModel.done:
            raise TypeError("yield value type error!")

    def process(self, task_id, item, callback, _id: int):
        iterators = callback(item)
        if not isgenerator(iterators):
            raise TypeError(f"{callback.__name__} function isn't a generator!")
        for it in iterators:
            self.distribute(task_id=task_id, item=it, _id=_id)

    @check_pause
    def spider(self):
        if task_item := self.task_queue.get_pending_task():
            seed = task_item.data
            status = Status.FINISHED
            task_id = task_item.task_id

            try:
                self.process(task_id=task_id, item=seed, callback=self.Crawler.request, _id=0)

            except Exception as e:

                seed.params.retry += 1
                url, _status = seed.url, e.__class__.__name__

                msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                if getattr(e, "response", None) and isinstance(e.response, Res):
                    url = e.response.request.url
                    _status = e.response.status_code

                self.spider_logging(seed, None, error=True, url=url, status=_status, msg=msg)

                if seed.params.retry < self.max_retries:
                    status = Status.PENDING

                elif self.record_failed:
                    try:
                        response = Response(seed, "failed", max_retries=True)
                        self.process(task_id=task_id, item=response, callback=self.Crawler.parse, _id=2)
                    except Exception as e:
                        msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                        logger.error(msg=msg)

            finally:
                self.task_queue.update_task(task_id, status=status, data=seed)

    def spider_logging(
            self, seed,
            item: Response = None,
            error: bool = False,
            dot: bool = True,
            **kwargs
    ):
        detail_log_info = LogTemplate.log_info(seed.to_dict)
        if error:
            url = kwargs.get("url")
            msg = kwargs.get("msg")
            status = kwargs.get("status")
            if dot:
                self.loghub_dot.build(
                    topic=urlparse(url).netloc,
                    data_size=-1, cost_time=-1,
                    status=status, url=url,
                    seed=seed.to_string,
                    proxy_type=seed.params.proxy_type,
                    proxy=seed.params.proxy,
                    project=self.project,
                    task=self.task, msg=msg,
                )
            logger.info(LogTemplate.download_exception.format(
                detail=detail_log_info,
                retry=seed.params.retry,
                priority=seed.params.priority,
                seed_version=seed.params.seed_version,
                identifier=seed.identifier or "",
                exception=msg
            ))
        else:
            logger.info(LogTemplate.download_info.format(
                detail=detail_log_info,
                retry=seed.params.retry,
                priority=seed.params.priority,
                seed_version=seed.params.seed_version,
                identifier=seed.identifier or "",
                status=item.response,
                response=LogTemplate.log_info(item.to_dict)
            ))
            if dot:
                end_time = time.time()
                stime = seed.params.start_time
                cost_time = end_time - stime if stime else -1
                topic = urlparse(item.response.request.url).netloc
                data_size = int(item.response.headers.get("content-length", 0))
                self.loghub_dot.build(
                    topic=topic, data_size=data_size, cost_time=cost_time,
                    status=200, seed=seed.to_string, url=item.response.url,
                    proxy=seed.params.proxy, proxy_type=seed.params.proxy_type,
                    project=self.project, task=self.task,
                )

    def run(self):
        self.callback_register(self.loghub_dot.build_run, tag="LoghubDot")
        for _ in range(self.thread_num):
            self.callback_register(self.spider, tag="Distributor")
