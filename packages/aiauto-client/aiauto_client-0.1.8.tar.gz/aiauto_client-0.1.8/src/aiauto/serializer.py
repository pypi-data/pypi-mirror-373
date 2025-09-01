import inspect
import json
from typing import Callable, Union, List, Optional


def serialize(objective: Callable) -> str:
    try:
        return inspect.getsource(objective)
    except (OSError, TypeError) as e:
        raise ValueError(
            "Serialize 실패 objective 함수는 파일로 저장되어야 합니다\n"
            "REPL/Jupyter Notebook에서는 %%writefile magic을 사용해서 local 에 file 로 저장하세요\n\n"
            "%%writefile objective.py\n"
            "def objective(trial):\n"
            "    # 함수 내용\n"
            "    ...\n\n"
            "그 다음:\n"
            "from objective import objective\n"
            "study.optimize(objective, ...)"
        ) from e


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
