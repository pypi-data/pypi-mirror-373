from .seed import Seed
from typing import Dict, Any
from collections import namedtuple


class ItemMeta(type):

    def __new__(cls, name: str, bases: tuple, dct: dict) -> type:
        new_class = super().__new__(cls, name, bases, dct)
        if name != "BaseItem":
            table = getattr(new_class, "__TABLE__")
            fields = getattr(new_class, "__FIELDS__")
            if not table or not fields:
                raise ValueError(f"Missing required attributes '__TABLE__' or '__FIELDS__' in class {name}")
            new_class.Data = namedtuple(table, fields)
        return new_class


class BaseItem(metaclass=ItemMeta):

    __TABLE__ = ""
    __FIELDS__ = ""

    def __init__(self, seed: Seed, **kwargs):
        self.seed = seed

        data = {}
        for key, value in kwargs.items():
            if key in self.__FIELDS__:
                data[key] = value
            else:
                setattr(self, key, value)

        try:
            self.data = self.Data(**data)
        except TypeError as e:
            raise ValueError(f"Invalid field values for Data: {e}") from e

    @property
    def to_dict(self) -> Dict[str, Any]:
        return self.data._asdict()

    @property
    def fields(self) -> tuple[str]:
        return self.data._fields

    @property
    def table(self) -> str:
        return self.Data.__name__

    def __setitem__(self, key: str, value: Any):
        setattr(self, key, value)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, None)

    def __getattr__(self, name: str) -> Any:
        return None


class CSVItem(BaseItem):

    __TABLE__ = "cobweb"
    __FIELDS__ = "data"

