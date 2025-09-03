from collections import deque
from typing import Any, Iterable, Union


class Queue:
    def __init__(self):
        """初始化队列"""
        self._queue = deque()

    @property
    def length(self) -> int:
        """返回队列长度"""
        return len(self._queue)

    def empty(self) -> bool:
        """检查队列是否为空"""
        return not self._queue

    def push(self, data: Union[Any, Iterable], direct_insertion: bool = False):
        """
        向队列中添加数据。
        如果数据是可迭代对象（如列表、元组或集合），可以选择直接扩展队列。
        """
        if not data:
            return

        if not direct_insertion and isinstance(data, (list, tuple, set)):
            self._queue.extend(data)
        else:
            self._queue.append(data)

    def pop(self) -> Any:
        """
        从队列左侧弹出一个元素。
        如果队列为空，返回 None。
        """
        try:
            return self._queue.popleft()
        except IndexError:
            return None

    def iter_items(self, limit: int = 1) -> Iterable:
        """
        按指定数量从队列中弹出多个元素并生成它们。
        如果队列为空或达到限制，则停止生成。
        """
        for _ in range(limit):
            item = self.pop()
            if item is None:
                break
            yield item