from typing import Generator, Optional, List
import traceback

from abc import ABCMeta, abstractmethod


class AdapterPluginError(Exception):
    """适配器插件错误"""

    def __init__(self, message: str):
        super().__init__(message)


class AdapterParseError(Exception):
    def __init__(self, original_exception):
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()
        super().__init__(f"{str(original_exception)}\nTraceback:\n{self.traceback}")


class AdapterABC(metaclass=ABCMeta):
    """用于解析服务端通过socket发送的数据帧"""

    @property
    @abstractmethod
    def adapter_code(self) -> str:
        pass

    @property
    @abstractmethod
    def adapter_name(self) -> str:
        pass

    @abstractmethod
    def parse(self, msg: str, userdata=None) -> Generator[dict, None, None]:
        pass


class AdapterNegotiation(object):
    """适配器代理通过适配器编码选择合适的适配器"""

    def __init__(self):
        self.adapters: List[AdapterABC] = []
        self.adapter_map = {}

    def select_adapter(self, adapter_code: str) -> Optional[AdapterABC]:
        return self.adapter_map.get(adapter_code)

    def register_adapter(self, adapter_instance: AdapterABC):
        self.adapter_map[adapter_instance.adapter_code] = adapter_instance
        self.adapters.append(adapter_instance)
