import os
import time
import threading
from typing import Callable
from cobweb.db import RedisDB, ApiDB
from cobweb.utils import check_pause
from cobweb.base import Seed, logger, TaskQueue, Status
from cobweb.constant import LogTemplate
from .scheduler import Scheduler
use_api = bool(os.getenv("REDIS_API_HOST", 0))


class RedisScheduler(Scheduler):

    def __init__(
            self,
            task,
            project,
            stop: threading.Event,
            pause: threading.Event,
            task_queue: TaskQueue,
            callback_register: Callable
    ):
        super().__init__(task, project, stop, pause, task_queue, callback_register)
        self.todo_key = f"{{{project}:{task}}}:todo"
        self.done_key = f"{{{project}:{task}}}:done"
        self.fail_key = f"{{{project}:{task}}}:fail"
        self.heartbeat_key = f"heartbeat:{project}_{task}"
        self.speed_control_key = f"speed_control:{project}_{task}"
        self.reset_lock_key = f"lock:reset:{project}_{task}"
        self.db = ApiDB() if use_api else RedisDB()

    def reset(self):
        """
        检查过期种子，重新添加到redis缓存中
        """
        while not self.stop.is_set():
            if self.db.lock(self.reset_lock_key, t=360):

                _min = -int(time.time()) + self.seed_reset_seconds
                self.db.members(self.todo_key, 0, _min=_min, _max="(0")
                self.db.delete(self.reset_lock_key)

            time.sleep(self.seed_reset_seconds)

    @check_pause
    def schedule(self):
        """
        调度任务，获取redis队列种子，同时添加到doing字典中
        """
        if not self.db.zcount(self.todo_key, 0, "(1000"):
            time.sleep(self.scheduler_wait_seconds)
            return

        if self.task_queue.status_length(Status.PENDING) >= self.todo_queue_size\
                or self.task_queue.length() > 5 * self.todo_queue_size:
            time.sleep(self.todo_queue_full_wait_seconds)
            return

        if members := self.db.members(
            self.todo_key, int(time.time()),
            count=self.todo_queue_size,
            _min=0, _max="(1000"
        ):
            for member, priority in members:
                seed = Seed(member, priority=int(priority % 1000))
                self.task_queue.add_task(
                    task_id=seed.sid,
                    data=seed,
                    status=Status.PENDING,
                    priority=seed.params.priority
                )

    @check_pause
    def insert(self):
        """
        添加新种子到redis队列中
        """
        if task_list := self.task_queue.get_task_by_status(
            status=Status.INSERT, limit=self.new_queue_max_size
        ):
            seed_info, task_ids = dict(), set()

            for task_item in task_list:
                seed = task_item.data
                task_ids.add(task_item.task_id)
                seed_info[seed.to_string] = seed.params.priority

            self.db.zadd(self.todo_key, seed_info, nx=True)
            self.task_queue.remove(task_ids)

        if self.task_queue.status_length(status=Status.INSERT) < self.new_queue_max_size:
            time.sleep(self.scheduler_wait_seconds)

    @check_pause
    def refresh(self):
        """
        刷新doing种子过期时间，防止reset重新消费
        """
        if task_list := self.task_queue.get_task_by_status(
            status=[Status.PENDING, Status.PROCESSING, Status.FINISHED],
        ):
            refresh_time = int(time.time())
            seed_info = {it.data.to_string: -refresh_time - it.data.params.priority / 1000 for it in task_list}
            self.db.zadd(self.todo_key, seed_info, xx=True)
        time.sleep(self.seed_reset_seconds // 3)

    @check_pause
    def delete(self):
        """
        删除队列种子，根据状态添加至成功或失败队列，移除doing字典种子索引
        """
        if task_list := self.task_queue.get_task_by_status(
                status=Status.FINISHED, limit=self.done_queue_max_size
        ):
            zrem_items = [it.data.to_string for it in task_list]
            remove_task_ids = [it.task_id for it in task_list]
            self.db.zrem(self.todo_key, *zrem_items)
            self.task_queue.remove(remove_task_ids)

        if self.task_queue.status_length(status=Status.FINISHED) < self.done_queue_max_size:
            time.sleep(self.done_queue_wait_seconds)

    def run(self):
        start_time = int(time.time())

        for func in [self.reset, self.insert, self.delete, self.refresh, self.schedule]:
            self.callback_register(func, tag="scheduler")

        while not self.stop.is_set():
            todo_len = self.task_queue.status_length(status=Status.PENDING)
            doing_len = self.task_queue.status_length(status=Status.PROCESSING)
            done_len = self.task_queue.status_length(status=Status.FINISHED)
            upload_len = self.task_queue.status_length(status=Status.UPLOAD)

            redis_doing_count = self.db.zcount(self.todo_key, "-inf", "(0")
            redis_todo_len = self.db.zcount(self.todo_key, 0, "(1000")
            redis_seed_count = self.db.zcard(self.todo_key)

            if self.pause.is_set():
                execute_time = int(time.time()) - start_time
                if not self.task_model and execute_time > self.before_scheduler_wait_seconds:
                    logger.info("Done! ready to close thread...")
                    self.stop.set()
                elif redis_todo_len:
                    logger.info(
                        f"Recovery {self.task} task run！"
                        f"Todo seeds count: {redis_todo_len}"
                        f", queue length: {redis_seed_count}"
                    )
                    self.pause.clear()
                else:
                    logger.info("Pause! waiting for resume...")

            elif self.task_queue.length() == 0:
                if redis_seed_count:
                    logger.info(
                        f"Todo seeds count: {redis_todo_len}"
                        f", queue length: {redis_seed_count}"
                    )
                    self.pause.clear()
                else:
                    count = 0
                    for _ in range(3):
                        if not redis_seed_count:
                            count += 1
                            time.sleep(5)
                            logger.info("Checking count...")
                        else:
                            break
                    if count >= 3:
                        logger.info("Todo queue is empty! Pause set...")
                        self.pause.set()

            else:
                logger.info(LogTemplate.launcher_pro_polling.format(
                    task=self.task,
                    doing_len=doing_len,
                    todo_len=todo_len,
                    done_len=done_len,
                    redis_seed_count=redis_seed_count,
                    redis_todo_len=redis_todo_len,
                    redis_doing_len=redis_doing_count,
                    upload_len=upload_len,
                ))

            time.sleep(30)
