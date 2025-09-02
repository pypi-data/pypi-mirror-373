import os
import importlib
from fastapi import APIRouter
from kxy.framework.mapper import Mapper
import inspect
def auto_regist_routes(package,prefix="/api")->APIRouter:
    '''自动注册路由
    package: 包名，例如引用路由为app.infra.api.xxx，则package为app.infra.api
    prefix: 路由前缀，例如路由为/api/system/user/update，则prefix为/api/system
    '''
    if not package:
        raise Exception("auto_regist_routes package is empty")
    router = APIRouter()
    # 获取调用者的文件帧
    caller_frame = inspect.currentframe().f_back
    # 获取调用者文件的目录路径
    caller_dir = os.path.dirname(os.path.abspath(caller_frame.f_code.co_filename))

    # 获取当前目录下所有.py文件（排除__init__.py）
    api_files = [f for f in os.listdir(caller_dir) if f.endswith(".py") and f != "__init__.py"]

    # 动态加载每个文件中的路由
    for file in api_files:
        module_name = file[:-3]  # 去掉.py后缀
        module = importlib.import_module(f".{module_name}", package=package)
        if hasattr(module, "router"):
            router.include_router(module.router, prefix=prefix)
    return router
def auto_regist_services(package)->list:
    '''自动将服务注册到Mapper中
    package: 包名，例如引用服务为app.infra.services.xxx，则package为app.infra.services
    '''
    # 获取调用者的文件帧
    caller_frame = inspect.currentframe().f_back
    # 获取调用者文件的目录路径
    caller_dir = os.path.dirname(os.path.abspath(caller_frame.f_code.co_filename))
    # 获取当前目录下所有.py文件（排除__init__.py）
    api_files = [f for f in os.listdir(caller_dir) if f.endswith(".py") and f != "__init__.py"]

    # 动态加载每个文件中的路由
    for file in api_files:
        module_name = file[:-3]  # 去掉.py后缀
        module = importlib.import_module(f".{module_name}", package=package)
        # 遍历模块中的所有成员
        for name, obj in inspect.getmembers(module):
            # 筛选出类对象，且属于当前模块（排除import的类）
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                Mapper.register(obj)