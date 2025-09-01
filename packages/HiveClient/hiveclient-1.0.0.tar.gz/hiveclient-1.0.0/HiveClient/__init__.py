# WeComMsg/__init__.py

# 从核心代码文件中导入需要对外暴露的类/函数
from .HiveClient import HiveClient, Retry

# 可选：定义版本号（与 setup.cfg 中的 version 一致）
__version__ = "1.0.0"

# 可选：明确指定包对外暴露的成员（规范导入）
__all__ = ["HiveClient", "Retry"]