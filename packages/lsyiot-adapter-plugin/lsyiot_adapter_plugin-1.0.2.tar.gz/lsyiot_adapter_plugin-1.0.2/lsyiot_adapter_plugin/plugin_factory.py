import os
import importlib
import inspect
import yaml
from lsyiot_adapter_plugin.negotiation import AdapterNegotiation, AdapterABC, AdapterPluginError


class PluginFactory(object):
    def __init__(self, plugins_dir: str):
        self.negotiation = AdapterNegotiation()
        self.plugins_dir = plugins_dir

    def load_adapters(self):
        """通过插件工厂的load_adapters方法，动态加载plugins目录下的所有适配器，并支持读取config.yml作为初始化参数"""

        if not os.path.exists(self.plugins_dir):
            raise AdapterPluginError(f"Plugins directory '{self.plugins_dir}' does not exist.")

        # 遍历plugins目录下的所有子目录
        for plugin_name in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, plugin_name)

            # 跳过__pycache__和非目录文件
            if not os.path.isdir(plugin_path) or plugin_name.startswith("__"):
                continue

            # 检查config.yml
            config_path = os.path.join(plugin_path, "config.yml")
            config_dict = None
            if os.path.isfile(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config_dict = yaml.safe_load(f)

            try:
                # 动态导入插件模块
                module_name = f"plugins.{plugin_name}"

                # 尝试导入插件目录下的Python文件
                for file_name in os.listdir(plugin_path):
                    if file_name.endswith(".py") and not file_name.startswith("__"):
                        module_file = file_name[:-3]  # 去掉.py后缀
                        full_module_name = f"{module_name}.{module_file}"

                        try:
                            module = importlib.import_module(full_module_name)

                            # 查找模块中所有实现了AdapterABC的类
                            for name, obj in inspect.getmembers(module, inspect.isclass):
                                if (
                                    issubclass(obj, AdapterABC)
                                    and obj != AdapterABC
                                    and obj.__module__ == full_module_name
                                ):
                                    # 实例化并注册适配器
                                    if config_dict is not None:
                                        adapter_instance = obj(config_dict)
                                    else:
                                        adapter_instance = obj()
                                    self.negotiation.register_adapter(adapter_instance)

                        except Exception as e:
                            raise AdapterPluginError(f"Failed to load module {full_module_name}: {e}") from e

            except Exception as e:
                raise AdapterPluginError(f"Failed to process plugin directory {plugin_name}: {e}") from e
