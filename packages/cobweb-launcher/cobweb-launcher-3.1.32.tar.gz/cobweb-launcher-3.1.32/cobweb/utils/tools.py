import re
import hashlib
import inspect
from typing import Union
from importlib import import_module


def md5(text: Union[str, bytes]) -> str:
    if isinstance(text, str):
        text = text.encode('utf-8')
    return hashlib.md5(text).hexdigest()


def dynamic_load_class(model_info):
    if isinstance(model_info, str):
        if "import" in model_info:
            model_path, class_name = re.search(
                r"from (.*?) import (.*?)$", model_info
            ).groups()
            model = import_module(model_path)
            class_object = getattr(model, class_name)
        else:
            model_path, class_name = model_info.rsplit(".", 1)
            model = import_module(model_path)
            class_object = getattr(model, class_name)
        return class_object
    elif inspect.isclass(model_info):
        return model_info
    raise TypeError()

