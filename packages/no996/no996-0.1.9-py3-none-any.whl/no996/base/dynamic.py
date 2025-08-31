import importlib.util
import sys


def load_function_from_file(file_path, function_name):
    """
    从指定Python文件中加载特定函数

    参数:
        file_path: Python文件路径
        function_name: 要加载的函数名

    返回:
        函数对象
    """
    # 生成唯一的模块名
    module_name = f"dynamic_module_{hash(file_path)}"

    # 创建模块规范
    spec = importlib.util.spec_from_file_location(module_name, file_path)

    # 创建并加载模块
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # 获取函数
    function = getattr(module, function_name)
    return function
