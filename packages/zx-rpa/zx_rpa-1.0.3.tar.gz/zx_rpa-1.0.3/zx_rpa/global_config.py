"""
全局YAML配置读写类
支持无限层级访问和修改，如 G.xx.xx.xx
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Union


class YamlConfigProxy:
    """YAML配置代理类，支持链式访问和字典操作"""

    def __init__(self, config_manager, path: List[str] = None):
        """
        初始化配置代理

        Args:
            config_manager: 配置管理器实例
            path: 当前访问路径
        """
        self._config_manager = config_manager
        self._path = path or []

    def __getattr__(self, name: str):
        """支持 G.xx.xx.xx 链式访问"""
        new_path = self._path + [name]
        value = self._config_manager._get_by_path(new_path)

        if isinstance(value, dict):
            # 如果是字典，返回新的代理对象继续链式访问
            return YamlConfigProxy(self._config_manager, new_path)
        else:
            # 如果是值，直接返回原生类型
            return value

    def __setattr__(self, name: str, value: Any):
        """支持 G.xx.xx = value 赋值"""
        if name.startswith('_'):
            # 内部属性直接设置
            super().__setattr__(name, value)
        else:
            # 配置属性，写入YAML
            new_path = self._path + [name]
            self._config_manager._set_by_path(new_path, value)

    def __getitem__(self, key: str):
        """支持字典式访问 G.xx['key']"""
        new_path = self._path + [key]
        value = self._config_manager._get_by_path(new_path)

        if isinstance(value, dict):
            return YamlConfigProxy(self._config_manager, new_path)
        else:
            return value

    def __setitem__(self, key: str, value: Any):
        """支持字典式赋值 G.xx['key'] = value"""
        new_path = self._path + [key]
        self._config_manager._set_by_path(new_path, value)

    def __contains__(self, key: str):
        """支持 'key' in G.xx 检查"""
        new_path = self._path + [key]
        return self._config_manager._get_by_path(new_path) is not None

    def __iter__(self):
        """支持 for key in G.xx 迭代"""
        value = self._config_manager._get_by_path(self._path)
        if isinstance(value, dict):
            return iter(value.keys())
        else:
            return iter([])

    def keys(self):
        """返回字典的键"""
        value = self._config_manager._get_by_path(self._path)
        if isinstance(value, dict):
            return value.keys()
        else:
            return []

    def values(self):
        """返回字典的值"""
        value = self._config_manager._get_by_path(self._path)
        if isinstance(value, dict):
            return value.values()
        else:
            return []

    def items(self):
        """返回字典的键值对"""
        value = self._config_manager._get_by_path(self._path)
        if isinstance(value, dict):
            return value.items()
        else:
            return []

    def get(self, key: str, default=None):
        """字典式获取值，支持默认值"""
        new_path = self._path + [key]
        value = self._config_manager._get_by_path(new_path)
        return value if value is not None else default

    def to_dict(self):
        """转换为真正的字典"""
        value = self._config_manager._get_by_path(self._path)
        if isinstance(value, dict):
            return value.copy()
        else:
            return {}

    def value(self):
        """获取原生Python类型的值"""
        return self._config_manager._get_by_path(self._path)

    def __repr__(self):
        """返回当前路径的值"""
        if not self._path:
            return f"<YamlConfig: {self._config_manager.config_file}>"

        value = self._config_manager._get_by_path(self._path)
        return repr(value)

    def __str__(self):
        """返回当前路径的值的字符串表示"""
        if not self._path:
            return f"YamlConfig({self._config_manager.config_file})"

        value = self._config_manager._get_by_path(self._path)
        return str(value)


class GlobalYamlConfig:
    """全局YAML配置管理器"""
    
    def __init__(self, config_file: str):
        """
        初始化全局配置管理器
        
        Args:
            config_file: YAML配置文件路径
        """
        self.config_file = Path(config_file)
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """加载YAML配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
            else:
                # 如果文件不存在，创建空配置
                self.config = {}
                self.save_config()
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            self.config = {}
    
    def save_config(self):
        """保存配置到YAML文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
    
    def _get_by_path(self, path: List[str]) -> Any:
        """根据路径获取配置值"""
        current = self.config
        
        try:
            for key in path:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None
    
    def _set_by_path(self, path: List[str], value: Any):
        """根据路径设置配置值"""
        if not path:
            return
        
        current = self.config
        
        # 导航到目标位置的父级
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                # 如果中间路径不是字典，转换为字典
                current[key] = {}
            current = current[key]
        
        # 设置最终值
        current[path[-1]] = value
        
        # 保存到文件
        self.save_config()
    
    def __getattr__(self, name: str):
        """支持 G.xx 访问"""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        value = self._get_by_path([name])

        if isinstance(value, dict):
            # 如果是字典，返回代理对象支持链式访问
            return YamlConfigProxy(self, [name])
        else:
            # 如果是值，直接返回原生类型
            return value
    
    def __setattr__(self, name: str, value: Any):
        """支持 G.xx = value 赋值"""
        if name.startswith('_') or name in ['config_file', 'config']:
            # 内部属性直接设置
            super().__setattr__(name, value)
        else:
            # 配置属性，写入YAML
            self._set_by_path([name], value)
    
    def get_all(self) -> Dict:
        """获取所有配置"""
        return self.config.copy()
    
    def reload(self):
        """重新加载配置文件"""
        self.load_config()


# 全局配置实例（需要在使用前初始化）
G = None


def init_global_config(config_file: str):
    """
    初始化全局配置
    
    Args:
        config_file: YAML配置文件路径
    """
    global G
    G = GlobalYamlConfig(config_file)
    return G
