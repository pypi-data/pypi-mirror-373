import time
import uuid
import inspect
import threading
import importlib

from cobweb import setting
from cobweb.launchers.uploader import Uploader
from cobweb.utils.tools import dynamic_load_class
from cobweb.launchers.distributor import Distributor
from cobweb.base import Seed, logger, TaskQueue, Status
from typing import Optional, Union, Dict, Any, Callable


class Launcher:

    __REGISTER_FUNC__: Dict[str, Callable] = {}
    __WORKER_THREAD__: Dict[str, threading.Thread] = {}

    def __init__(self, task, project, custom_setting=None, **kwargs):
        super().__init__()

        self.task = task
        self.project = project

        self._app_time = int(time.time())
        self._stop = threading.Event()  # 结束事件
        self._pause = threading.Event()  # 暂停事件

        _setting = self._load_custom_settings(custom_setting)

        _setting.update(kwargs)
        for key, value in _setting.items():
            setattr(setting, key.upper(), value)

        self._done_model = setting.DONE_MODEL
        self._task_model = setting.TASK_MODEL

        self._task_queue = TaskQueue()

        self.Scheduler = dynamic_load_class(setting.SCHEDULER)
        self.SpiderCrawler = dynamic_load_class(setting.CRAWLER)
        self.SpiderPipeline = dynamic_load_class(setting.PIPELINE)

    @staticmethod
    def _load_custom_settings(custom_setting: Optional[Union[str, Dict]]) -> Dict[str, Any]:
        _setting = {}
        if custom_setting:
            if isinstance(custom_setting, dict):
                _setting = custom_setting
            elif isinstance(custom_setting, str):
                module = importlib.import_module(custom_setting)
                _setting = {
                    k: v
                    for k, v in module.__dict__.items()
                    if not k.startswith("__") and not inspect.ismodule(v)
                }
            else:
                raise ValueError("custom_setting must be a dictionary or a module path.")
        return _setting

    @property
    def request(self):
        """
        自定义request函数
        use case:
            from cobweb.base import Request, BaseItem
            @launcher.request
            def request(seed: Seed) -> Union[Request, BaseItem]:
                ...
                yield Request(seed.url, seed)
        """
        def decorator(func):
            self.SpiderCrawler.request = func
        return decorator

    @property
    def download(self):
        """
        自定义download函数
        use case:
            from cobweb.base import Request, Response, Seed, BaseItem
            @launcher.download
            def download(item: Request) -> Union[Seed, BaseItem, Response, str]:
                ...
                yield Response(item.seed, response)
        """
        def decorator(func):
            self.SpiderCrawler.download = func
        return decorator

    @property
    def parse(self):
        """
        自定义parse函数, xxxItem为自定义的存储数据类型
        use case:
            from cobweb.base import Request, Response
            @launcher.parse
            def parse(item: Response) -> BaseItem:
               ...
               yield xxxItem(seed, **kwargs)
        """
        def decorator(func):
            self.SpiderCrawler.parse = func
        return decorator

    def start_seeds(self, seeds: list[Union[str, Dict]]) -> list[Seed]:
        seed_list = [Seed(seed) for seed in seeds]
        for seed in seed_list:
            self._task_queue.add_task(
                task_id=seed.sid,
                data=seed,
                status=Status.PENDING,
                priority=seed.params.priority,
                parent_id=None,
                ttl_seconds=None
            )
        return seed_list

    def _register(self, func: Callable, tag: str = "launcher"):
        name = f"{tag}:{func.__name__}_{uuid.uuid4()}"
        self.__REGISTER_FUNC__[name] = func
        if not self.__WORKER_THREAD__.get(name):
            worker_thread = threading.Thread(name=name, target=func)
            self.__WORKER_THREAD__[name] = worker_thread

    def _monitor(self):
        while not self._stop.is_set():
            if not self._pause.is_set():
                for name, worker_thread in list(self.__WORKER_THREAD__.items()):
                    if not worker_thread.is_alive():
                        logger.debug(f"{name} thread is dead. Restarting...")
                        func = self.__REGISTER_FUNC__[name]
                        worker_thread = threading.Thread(name=name, target=func)
                        self.__WORKER_THREAD__[name] = worker_thread
                        worker_thread.start()
            time.sleep(15)
        logger.info("monitor thread close!")

    def start(self):
        self._pause.is_set()

        self.Scheduler(
            task=self.task,
            project=self.project,
            stop=self._stop,
            pause=self._pause,
            task_queue=self._task_queue,
            callback_register=self._register
        ).start()

        Distributor(
            task=self.task,
            project=self.project,
            task_queue=self._task_queue,
            callback_register=self._register,
            stop=self._stop, pause=self._pause,
            SpiderCrawler=self.SpiderCrawler
        ).start()

        Uploader(
            task=self.task, project=self.project,
            stop=self._stop, pause=self._pause,
            task_queue=self._task_queue,
            callback_register=self._register,
            SpiderPipeline=self.SpiderPipeline
        ).start()

        self._monitor()
        logger.info("task done!")

