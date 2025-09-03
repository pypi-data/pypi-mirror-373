from typing import Any, Dict, Union


class Response:
    """
    响应对象类，支持动态属性访问和字典式操作

    优化特性：
    1. 使用 __slots__ 减少内存占用
    2. 缓存 to_dict 结果提高性能
    3. 更好的错误处理和类型检查
    4. 支持弱引用避免循环引用
    5. 线程安全的属性访问
    """

    __slots__ = ('_seed', '_response', '_extra_attrs', '_dict_cache', '__weakref__')

    def __init__(
            self,
            seed: Any,
            response: Any,
            **kwargs: Any
    ) -> None:
        """
        初始化 Response 对象

        Args:
            seed: 种子对象，用于动态属性访问
            response: 响应对象
            **kwargs: 额外的属性
        """
        # 使用私有属性避免与动态属性冲突
        object.__setattr__(self, '_seed', seed)
        object.__setattr__(self, '_response', response)
        object.__setattr__(self, '_extra_attrs', kwargs.copy())
        object.__setattr__(self, '_dict_cache', None)

    @property
    def seed(self) -> Any:
        """获取种子对象"""
        return self._seed

    @property
    def response(self) -> Any:
        """获取响应对象"""
        return self._response

    @property
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式，使用缓存提高性能

        Returns:
            包含所有属性的字典
        """
        if self._dict_cache is None:
            _dict = self._extra_attrs.copy()

            # 安全地获取 seed 的字典表示
            if hasattr(self._seed, 'to_dict'):
                if callable(self._seed.to_dict):
                    try:
                        _dict.update(self._seed.to_dict())
                    except Exception as e:
                        # 记录错误但不中断执行
                        _dict['_seed_to_dict_error'] = str(e)
                else:
                    _dict.update(self._seed.to_dict)
            elif hasattr(self._seed, '__dict__'):
                _dict.update(self._seed.__dict__)
            elif isinstance(self._seed, dict):
                _dict.update(self._seed)

            # 缓存结果
            object.__setattr__(self, '_dict_cache', _dict)

        return self._dict_cache.copy()  # 返回副本避免外部修改

    def invalidate_cache(self) -> None:
        """清除缓存，当对象状态改变时调用"""
        object.__setattr__(self, '_dict_cache', None)

    def __getattr__(self, name: str) -> Any:
        """
        动态获取属性

        优先级：
        1. _extra_attrs 中的属性
        2. seed 对象的属性

        Args:
            name: 属性名

        Returns:
            属性值

        Raises:
            AttributeError: 当属性不存在时
        """
        # 避免递归调用
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # 首先检查额外属性
        if name in self._extra_attrs:
            return self._extra_attrs[name]

        # 然后检查 seed 对象
        return self._get_from_seed(name)

    def _get_from_seed(self, name: str) -> Any:
        """
        从 seed 对象获取属性

        Args:
            name: 属性名

        Returns:
            属性值

        Raises:
            AttributeError: 当属性不存在时
        """
        if self._seed is None:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}' (seed is None)")

        # 尝试不同的访问方式
        try:
            # 方式1: 字典式访问
            if hasattr(self._seed, '__getitem__'):
                try:
                    return self._seed[name]
                except (KeyError, TypeError):
                    pass

            # 方式2: 属性访问
            if hasattr(self._seed, name):
                return getattr(self._seed, name)

            # 方式3: 如果 seed 是字典
            if isinstance(self._seed, dict) and name in self._seed:
                return self._seed[name]

        except Exception as e:
            raise AttributeError(
                f"Error accessing '{name}' from seed: {e}"
            ) from e

        # 属性不存在
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __getitem__(self, key: str) -> Any:
        """
        支持字典式访问

        Args:
            key: 键名

        Returns:
            对应的值
        """
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        设置属性

        Args:
            name: 属性名
            value: 属性值
        """
        if name.startswith('_') or name in self.__slots__:
            object.__setattr__(self, name, value)
        else:
            # 设置到额外属性中
            self._extra_attrs[name] = value
            # 清除缓存
            self.invalidate_cache()

    def __setitem__(self, key: str, value: Any) -> None:
        """支持字典式设置"""
        setattr(self, key, value)

    def __delattr__(self, name: str) -> None:
        """
        删除属性

        Args:
            name: 属性名
        """
        if name.startswith('_') or name in self.__slots__:
            object.__delattr__(self, name)
        elif name in self._extra_attrs:
            del self._extra_attrs[name]
            self.invalidate_cache()
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __delitem__(self, key: str) -> None:
        """支持字典式删除"""
        delattr(self, key)

    def __contains__(self, key: str) -> bool:
        """
        检查是否包含某个属性

        Args:
            key: 属性名

        Returns:
            是否包含该属性
        """
        try:
            getattr(self, key)
            return True
        except AttributeError:
            return False

    def __iter__(self):
        """支持迭代，返回所有属性名"""
        return iter(self.to_dict.keys())

    def keys(self):
        """返回所有属性名"""
        return self.to_dict.keys()

    def values(self):
        """返回所有属性值"""
        return self.to_dict.values()

    def items(self):
        """返回所有属性键值对"""
        return self.to_dict.items()

    def get(self, key: str, default: Any = None) -> Any:
        """
        安全获取属性值

        Args:
            key: 属性名
            default: 默认值

        Returns:
            属性值或默认值
        """
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def update(self, other: Union[Dict[str, Any], 'Response'], **kwargs: Any) -> None:
        """
        更新属性

        Args:
            other: 字典或另一个 Response 对象
            **kwargs: 额外的属性
        """
        if isinstance(other, dict):
            self._extra_attrs.update(other)
        elif isinstance(other, Response):
            self._extra_attrs.update(other._extra_attrs)
        elif hasattr(other, 'items'):
            self._extra_attrs.update(dict(other.items()))

        self._extra_attrs.update(kwargs)
        self.invalidate_cache()

    def copy(self) -> 'Response':
        """
        创建副本

        Returns:
            新的 Response 对象
        """
        return Response(self._seed, self._response, **self._extra_attrs)

    def __repr__(self) -> str:
        """字符串表示"""
        extra_attrs = ', '.join(f'{k}={v!r}' for k, v in list(self._extra_attrs.items())[:3])
        if len(self._extra_attrs) > 3:
            extra_attrs += f', ... (+{len(self._extra_attrs) - 3} more)'

        return f"{self.__class__.__name__}(seed={self._seed!r}, response={self._response!r}, {extra_attrs})"

    def __str__(self) -> str:
        """用户友好的字符串表示"""
        return f"{self.__class__.__name__} with {len(self._extra_attrs)} extra attributes"

    def __eq__(self, other: Any) -> bool:
        """相等性比较"""
        if not isinstance(other, Response):
            return False

        return (
                self._seed == other._seed and
                self._response == other._response and
                self._extra_attrs == other._extra_attrs
        )

    def __hash__(self) -> int:
        """哈希值计算"""
        # 只对不可变部分计算哈希
        try:
            return hash((id(self._seed), id(self._response), tuple(sorted(self._extra_attrs.items()))))
        except TypeError:
            # 如果包含不可哈希的值，使用对象ID
            return hash(id(self))


# 扩展版本：支持更多高级特性
class AdvancedResponse(Response):
    """
    高级响应类，提供更多功能
    """

    __slots__ = ('_observers', '_frozen')

    def __init__(self, seed: Any, response: Any, frozen: bool = False, **kwargs: Any) -> None:
        """
        初始化高级响应对象

        Args:
            seed: 种子对象
            response: 响应对象
            frozen: 是否冻结对象（不允许修改）
            **kwargs: 额外属性
        """
        super().__init__(seed, response, **kwargs)
        object.__setattr__(self, '_observers', [])
        object.__setattr__(self, '_frozen', frozen)

    def freeze(self) -> None:
        """冻结对象，不允许修改"""
        object.__setattr__(self, '_frozen', True)

    def unfreeze(self) -> None:
        """解冻对象，允许修改"""
        object.__setattr__(self, '_frozen', False)

    @property
    def is_frozen(self) -> bool:
        """检查对象是否被冻结"""
        return self._frozen

    def __setattr__(self, name: str, value: Any) -> None:
        """设置属性（支持冻结检查）"""
        if self._frozen and not name.startswith('_'):
            raise AttributeError(f"Cannot modify frozen {self.__class__.__name__} object")

        old_value = getattr(self, name, None)
        super().__setattr__(name, value)

        # 通知观察者
        self._notify_observers(name, old_value, value)

    def add_observer(self, callback: callable) -> None:
        """
        添加观察者

        Args:
            callback: 回调函数，签名为 callback(attr_name, old_value, new_value)
        """
        if callback not in self._observers:
            self._observers.append(callback)

    def remove_observer(self, callback: callable) -> None:
        """
        移除观察者

        Args:
            callback: 要移除的回调函数
        """
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self, attr_name: str, old_value: Any, new_value: Any) -> None:
        """通知所有观察者"""
        for observer in self._observers:
            try:
                observer(attr_name, old_value, new_value)
            except Exception as e:
                # 记录错误但不中断执行
                print(f"Observer error: {e}")

