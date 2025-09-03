import json
import time
import hashlib
from typing import Any, Dict, Optional, Union


class SeedParams:
    """
    定义种子参数类，用于存储种子的元信息。
    """

    def __init__(
        self,
        retry: Optional[int] = None,
        priority: Optional[int] = None,
        seed_version: Optional[int] = None,
        seed_status: Optional[str] = None,
        proxy_type: Optional[str] = None,
        proxy: Optional[str] = None,
    ):
        self.retry = retry or 0
        self.priority = priority or 300
        self.seed_version = seed_version or int(time.time())
        self.seed_status = seed_status
        self.proxy_type = proxy_type
        self.proxy = proxy

    def __getattr__(self, name: str) -> Any:
        """动态获取未定义的属性，返回 None"""
        return None


class Seed:
    """
    种子类，用于表示一个种子对象，包含种子的基本属性和方法。
    """

    __SEED_PARAMS__ = [
        "retry",
        "priority",
        "seed_version",
        "seed_status",
        "proxy_type",
        "proxy",
    ]

    def __init__(
        self,
        seed: Union[str, bytes, Dict[str, Any]] = None,
        sid: Optional[str] = None,
        retry: Optional[int] = None,
        priority: Optional[int] = None,
        seed_version: Optional[int] = None,
        seed_status: Optional[str] = None,
        proxy_type: Optional[str] = None,
        proxy: Optional[str] = None,
        **kwargs,
    ):
        """
        初始化种子对象。
        :param seed: 种子数据，可以是字符串、字节或字典。
        :param sid: 种子的唯一标识符。
        :param retry: 重试次数。
        :param priority: 优先级。
        :param seed_version: 种子版本。
        :param seed_status: 种子状态。
        :param proxy_type: 代理类型。
        :param proxy: 代理地址。
        :param kwargs: 其他扩展参数。
        """
        # 初始化种子数据
        if seed:
            if isinstance(seed, (str, bytes)):
                try:
                    item = json.loads(seed)
                    self._init_seed(item)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON format for seed: {seed}") from e
            elif isinstance(seed, dict):
                self._init_seed(seed)
            else:
                raise TypeError(f"Seed type error, must be str, bytes, or dict! Seed: {seed}")

        # 初始化种子参数
        seed_params = {
            "retry": retry,
            "priority": priority,
            "seed_version": seed_version,
            "seed_status": seed_status,
            "proxy_type": proxy_type,
            "proxy": proxy,
        }

        # 合并扩展参数
        if kwargs:
            self._init_seed(kwargs)
            seed_params.update({k: v for k, v in kwargs.items() if k in self.__SEED_PARAMS__})

        # 初始化唯一标识符
        if sid or not getattr(self, "sid", None):
            self._init_id(sid)

        # 设置参数对象
        self.params = SeedParams(**seed_params)

    def __getattr__(self, name: str) -> Any:
        """动态获取未定义的属性，返回 None"""
        return None

    def __setitem__(self, key: str, value: Any):
        """支持字典式设置属性"""
        setattr(self, key, value)

    def __getitem__(self, key: str) -> Any:
        """支持字典式获取属性"""
        return getattr(self, key, None)

    def __str__(self) -> str:
        """返回种子的 JSON 字符串表示"""
        return self.to_string

    def __repr__(self) -> str:
        """返回种子的调试字符串表示"""
        attrs = [f"{k}={v}" for k, v in self.__dict__.items()]
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    def _init_seed(self, seed_info: Dict[str, Any]):
        """初始化种子数据"""
        for key, value in seed_info.items():
            if key not in self.__SEED_PARAMS__:
                self.__setattr__(key, value)

    def _init_id(self, sid: Optional[str]):
        """初始化种子的唯一标识符"""
        if not sid:
            sid = hashlib.md5(self.to_string.encode()).hexdigest()
        self.__setattr__("sid", sid)

    @property
    def to_dict(self) -> Dict[str, Any]:
        """返回种子的字典表示（不包含 params 属性）"""
        seed = self.__dict__.copy()
        seed.pop("params", None)
        return seed

    @property
    def to_string(self) -> str:
        """返回种子的紧凑 JSON 字符串表示"""
        return json.dumps(
            self.to_dict,
            ensure_ascii=False,
            separators=(",", ":")
        )

    @property
    def get_all(self) -> str:
        """返回种子的所有属性（包括 params）的 JSON 字符串表示"""
        return json.dumps(
            self.__dict__,
            ensure_ascii=False,
            separators=(",", ":")
        )
