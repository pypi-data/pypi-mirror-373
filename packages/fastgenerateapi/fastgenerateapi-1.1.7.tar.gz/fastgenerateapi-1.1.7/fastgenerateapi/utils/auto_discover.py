import importlib
import os
from pathlib import Path
from typing import Optional, List


def get_path_list(path: str, match_prefix: str, prefix: str = "") -> List[str]:
    files = []
    prefix = prefix + "." + os.path.basename(path) if prefix else os.path.basename(path)
    for item in Path(path).iterdir():
        if item.is_file():
            if item.name.startswith(match_prefix) and item.name.endswith(".py"):
                files.append(prefix+"."+item.name[:-3])
        elif item.is_dir():
            if item.name.startswith(match_prefix):
                for s_item in Path(os.path.join(path, item.name)).iterdir():
                    if s_item.is_file() and s_item.name.startswith(match_prefix):
                        files.append(prefix + "." + item.name + "." + s_item.name[:-3])
            else:
                files += get_path_list(os.path.join(path, item.name), match_prefix, prefix)

    return files


def discover_models(
        base_path="apps",  # 模块路径
        include: Optional[List[str]] = None,  # 包含的模型
        exclude: Optional[List[str]] = None,  # 排除的模型
) -> List[str]:
    """
    自动发现models，并生成tortoise-orm所需要的字符串
    会自动添加 aerich.models，如不需要请在 exclude 参数排除
    """
    models_list = ["aerich.models"] + get_path_list(base_path, "models")
    return include + [model for model in models_list if model not in exclude] if exclude else models_list


def discover_routes(
        app,  # Fastapi 生成的实体类
        base_path="apps",  # 模块路径
        prefix="",  # 路由前缀
        include: Optional[List[str]] = None,  # 包含的路由
        exclude: Optional[List[str]] = None,  # 排除的路由
):
    """自动发现路由，并注册"""
    paths = include if include else []

    for path in paths + get_path_list(base_path, "router"):
        if exclude and path in exclude:
            continue
        module = importlib.import_module(path)
        if hasattr(module, "router"):
            app.include_router(prefix=prefix, router=getattr(module, "router"))
    return app


if __name__ == '__main__':
    # print(discover_models("../../modules"))
    print(get_path_list("../../modules", "router"))


