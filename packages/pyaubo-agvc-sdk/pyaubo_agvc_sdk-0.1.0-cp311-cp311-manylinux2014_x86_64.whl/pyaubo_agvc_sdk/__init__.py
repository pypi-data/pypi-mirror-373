import os, sys, ctypes
# 1. 找到 libagvc_sdk.so 并提前加载
_pkg_dir = os.path.dirname(__file__)
_so_path = os.path.join(_pkg_dir, "libagvc_sdk.so")

if os.path.exists(_so_path):
    ctypes.CDLL(_so_path, mode=ctypes.RTLD_GLOBAL)
else:
    raise ImportError(f"[pyaubo_agvc_sdk] libagvc_sdk.so not found in {_pkg_dir}")

# 2. 导入 pybind11 生成的实际 C++ 扩展模块
from . import pyaubo_agvc_sdk as _ext_module

# 3. 把 C++ 扩展里的所有符号（RpcClient 等）暴露到包顶层
globals().update({
    name: getattr(_ext_module, name)
    for name in dir(_ext_module) if not name.startswith("_")
})

# 清理内部引用
del _ext_module, os, ctypes
