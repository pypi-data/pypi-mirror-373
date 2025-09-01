import inspect
import json
from typing import Callable, Union, List, Optional


def serialize(objective: Callable) -> str:
    try:
        return inspect.getsource(objective)
    except Exception as e:
        raise ValueError("objective는 모듈 최상위 def만 허용합니다(데코레이터/로컬/람다 불가)") from e


def build_requirements(file_path: Optional[str] = None, reqs: Optional[List[str]] = None) -> str:
    if file_path and reqs:
        raise ValueError("requirements_file과 requirements_list는 동시에 지정할 수 없습니다")
    
    if file_path:
        with open(file_path, 'r') as f:
            return f.read()
    elif reqs:
        return "\n".join(reqs)
    else:
        return ""


def object_to_json(obj: Union[object, dict, None]) -> str:
    if obj is None:
        return ""
    
    if isinstance(obj, dict):
        return json.dumps(obj)
    
    cls = type(obj)
    module_name = cls.__module__
    class_name = cls.__name__
    
    if not module_name.startswith('optuna.'):
        raise ValueError(f"optuna 코어 클래스만 지원합니다: {class_name}")
    
    sig = inspect.signature(cls)
    kwargs = {}
    
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
        if hasattr(obj, param_name):
            value = getattr(obj, param_name)
            if param.default != value:
                kwargs[param_name] = value
    
    return json.dumps({
        "module": module_name,
        "class": class_name,
        "kwargs": kwargs
    })