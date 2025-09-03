import time
import threading
from enum import Enum
from hashlib import md5
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


class Status(Enum):
    PENDING = 0     # 待处理
    PROCESSING = 1  # 处理中
    FINISHED = 2    # 已完成
    INSERT = 3      # 新增
    UPLOAD = 4     # 上传


@dataclass
class Task:
    task_id: str         # 种子唯一ID
    data: Any            # 种子内容
    status: Status       # 当前状态
    priority: int            # 优先级（数值越小越优先）
    created_at: float        # 创建时间戳
    parent_id: Optional[str] = None   # 父种子 ID
    children_ids: List[str] = None    # 子种子 ID 列表
    ttl_seconds: Optional[int] = None  # 可选 TTL 时间（秒）

    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []


class TaskQueue:

    def __init__(self, cleanup_interval=60):
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()
        # self.cleanup_interval = cleanup_interval
        # self._start_cleanup_task()

    # def _start_cleanup_task(self):
    #     """启动后台线程清理过期种子"""
    #     def run():
    #         while True:
    #             time.sleep(self.cleanup_interval)
    #             self._cleanup_expired_seeds()
    #     threading.Thread(target=run, daemon=True).start()

    def length(self) -> int:
        with self._lock:
            return len(self._tasks)

    def status_length(self, status) -> int:
        with self._lock:
            return len([it for it in self._tasks.values() if it.status == status])

    def get_task(self, task_id) -> Task:
        with self._lock:
            if task_id in self._tasks:
                return self._tasks[task_id]

    def get_task_by_status(self, status: list, limit: int = None) -> List[Task]:
        with self._lock:
            if not isinstance(status, list):
                status = [status]
            task_list = [it for it in self._tasks.values() if it.status in status]
            task_list.sort(key=lambda x: (x.priority, x.created_at))
            return task_list[:limit] if limit else task_list

    def get_pending_task(self) -> Task:
        with self._lock:
            if items := [it for it in self._tasks.values() if it.status == Status.PENDING]:
                items.sort(key=lambda x: (x.priority, x.created_at))
                task_item = items[0]
                task_item.status = Status.PROCESSING
                self._tasks[task_item.task_id] = task_item
                return task_item

    def pop_task(self, status) -> Task:
        with self._lock:
            if items := [it for it in self._tasks.values() if it.status == status]:
                items.sort(key=lambda x: (x.priority, x.created_at))
                task_item = items[0]

                to_remove = set()
                queue = [task_item.task_id]

                while queue:
                    current = queue.pop(0)
                    if current in self._tasks:
                        to_remove.add(current)
                        queue.extend(self._tasks[current].children_ids)
                        del self._tasks[current]

                for tid in to_remove:
                    if task_item := self._tasks.get(tid):
                        if task_item.parent_id in self._tasks:
                            if tid in self._tasks[task_item.parent_id].children_ids:
                                self._tasks[task_item.parent_id].children_ids.remove(tid)

    def add_task(
            self,
            task_id: str = None,
            data: Any = None,
            status=Status.PENDING,
            priority: int = 500,
            parent_id: Optional[str] = None,
            ttl_seconds: Optional[int] = None
    ) -> bool:
        """添加新种子，可指定父种子"""
        with self._lock:
            if not task_id:
                task_id = md5(str(time.time()).encode()).hexdigest()

            if task_id in self._tasks:
                return False  # 防止重复添加

            task_item = Task(
                task_id=task_id,
                data=data,
                status=status,
                priority=priority,
                created_at=int(time.time()),
                parent_id=parent_id,
                ttl_seconds=ttl_seconds
            )
            self._tasks[task_id] = task_item

            if parent_id and parent_id in self._tasks:
                self._tasks[parent_id].children_ids.append(task_id)

            return True

    def update_task(self, task_id, status, data=None) -> Task:
        with self._lock:
            task_item = self._tasks[task_id]
            task_item.status = status
            if data:
                task_item.data = data

            if task_item.status != Status.FINISHED:
                for tid in task_item.children_ids:
                    if self._tasks[tid].status == Status.INSERT:
                        del self._tasks[tid]

            task_item.children_ids = []
            self._tasks[task_id] = task_item

            return task_item

    def remove(self, task_ids: list) -> bool:
        with self._lock:
            for task_id in task_ids:
                if task_item := self._tasks.get(task_id):

                    if task_item.children_ids:
                        continue

                    if task_item.parent_id in self._tasks:
                        if task_id in self._tasks[task_item.parent_id].children_ids:
                            self._tasks[task_item.parent_id].children_ids.remove(task_id)

                    del self._tasks[task_id]

    def count_children(self, task_id: str) -> int:
        with self._lock:
            if task_id in self._tasks:
                return len(self._tasks[task_id].children_ids)
            return 0

    # def _cleanup_expired_seeds(self):
    #     now = time.time()
    #     expired_ids = []
    #     with self._lock:
    #         for seed_id, seed in self._seeds.items():
    #             if seed.ttl_seconds and now - seed.created_at > seed.ttl_seconds:
    #                 expired_ids.append(seed_id)
    #         for seed_id in expired_ids:
    #             self._seeds[seed_id] = self._seeds[seed_id]._replace(status=SeedStatus.EXPIRED)
    #         print(f"清理了 {len(expired_ids)} 个过期种子")
