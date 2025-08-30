# lsyiot_adapter_plugin

一个用于 lsyiot_adpter_hub 数据适配器的插件系统，支持动态加载和注册各种设备数据适配器。

## 项目简介

本项目提供了一个灵活的适配器插件框架，允许开发者创建自定义的数据适配器来解析和转换来自不同 IoT 设备的数据格式。

## 核心组件

- `AdapterABC`: 抽象基类，定义了适配器的基本接口
- `AdapterNegotiation`: 适配器协商器，负责管理和选择适配器
- `PluginFactory`: 插件工厂，负责动态加载适配器插件
- `AdapterParseError`: 适配器解析异常类
- `AdapterPluginError`: 适配器插件异常类

## 安装

```bash
pip install lsyiot_adpter_plugin
```

## 快速开始

### 1. 创建自定义适配器

要创建一个自定义适配器，您需要继承 `AdapterABC` 类并实现必要的方法：

```python
# coding: utf-8
"""
倾角监测适配器
"""
import json
from datetime import datetime
from typing import Generator

from lsyiot_adapter_plugin.negotiation import AdapterABC, AdapterParseError


class MonitorTiltAdapter(AdapterABC):
    """倾角适配器"""

    def __init__(self):
        super().__init__()

    @property
    def adapter_code(self) -> str:
        return "MonitorTilt"

    @property
    def adapter_name(self) -> str:
        return "倾斜监测"

    def parse(self, msg, userdata=None) -> Generator[dict, None, None]:
        """
        解析消息并生成数据

        :param msg: 消息字符串
        :param userdata: 用户数据
        :return: 生成器，yield 解析后的数据字典
        """
        try:
            data = json.loads(msg)
            params = data.get("params", {})
            device_id = params.get("id", None)
            r_data = params.get("r_data", [])

            tm = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            send_data = {}

            # 构建发送数据结构
            for item in r_data:
                name = item.get("name", "")
                device = name[0]
                value_type = name[1:]
                value = float(item.get("value", 0))

                device_code = f"{device_id}-{device}"
                if device_code not in send_data:
                    send_data[device_code] = {
                        "device_code": device_code,
                        "x_displacement": 0.0,
                        "y_displacement": 0.0,
                        "z_displacement": 0.0,
                        "height": 0.0,
                    }

                if value_type == "X-CZ":
                    send_data[device_code]["x_displacement"] = value
                elif value_type == "Y-CZ":
                    send_data[device_code]["y_displacement"] = value
                elif value_type == "Z-CZ":
                    send_data[device_code]["z_displacement"] = value
                elif value_type == "Z":
                    send_data[device_code]["height"] = value

            for item in send_data.values():
                device_code = item["device_code"]
                row = {
                    "station_id": device_code,
                    "device_id": device_code,
                    "device_sn": device_code,
                    "collection_time": tm,
                    "x_displacement": item["x_displacement"],
                    "y_displacement": item["y_displacement"],
                    "z_displacement": item["z_displacement"],
                    "height": item["height"],
                    "sensor": device_code,
                }
                yield {"topic": userdata.get("topic_name") if userdata else None, "payload": row}
        except Exception as ex:
            raise AdapterParseError(ex)
```

### 2. 使用插件工厂加载适配器

```python
from lsyiot_adpter_plugin.plugin_factory import PluginFactory

# 初始化插件工厂
plugin_factory = PluginFactory("plugins")

# 加载所有适配器
plugin_factory.load_adapters()

# 获取协商器
negotiation = plugin_factory.negotiation

# 选择适配器
adapter = negotiation.select_adapter("MonitorTilt")

if adapter:
    # 解析数据
    sample_data = {
        "params": {
            "id": "device001",
            "r_data": [
                {"name": "AX-CZ", "value": "1.23"},
                {"name": "AY-CZ", "value": "2.34"},
                {"name": "AZ-CZ", "value": "3.45"},
                {"name": "AZ", "value": "4.56"}
            ]
        }
    }
    
    userdata = {"topic_name": "tilt_monitoring"}
    
    for result in adapter.parse(json.dumps(sample_data), userdata):
        print(result)
```

### 3. 目录结构

推荐的插件目录结构：

```
plugins/
├── monitor_tilt/
│   └── tilt_adapter.py
├── temperature/
│   └── temp_adapter.py
└── pressure/
    └── pressure_adapter.py
```

## API 参考

### AdapterABC

抽象基类，所有适配器都必须继承此类。

#### 属性

- `adapter_code` (str): 适配器唯一标识符
- `adapter_name` (str): 适配器显示名称

#### 方法

- `parse(msg, userdata=None)`: 解析消息的抽象方法

### AdapterNegotiation

适配器协商器，管理已注册的适配器。

#### 方法

- `register_adapter(adapter_instance)`: 注册适配器实例
- `select_adapter(adapter_code)`: 根据编码选择适配器

### PluginFactory

插件工厂，负责动态加载适配器。

#### 方法

- `__init__(plugins_dir)`: 初始化，指定插件目录
- `load_adapters()`: 加载插件目录下的所有适配器

## 异常处理

- `AdapterParseError`: 适配器解析数据时发生的错误
- `AdapterPluginError`: 插件加载或管理时发生的错误

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

