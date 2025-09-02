

try:
    # 尝试导入新版本的BaseSettings
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        # 如果失败，尝试导入旧版本的BaseSettings
        from pydantic import BaseSettings
    except ImportError:
        # 如果两种方式都失败，抛出明确的错误信息
        raise ImportError(
            "Could not import BaseSettings. "
            "Please install either pydantic<2.0 (for older version) or pydantic-settings (for newer version)."
        )

