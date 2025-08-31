import os,re,platform,sys
from pathlib import Path
from typing import Dict, Any

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from util.BluesResource import BluesResource

class ConfigManager:
    def __init__(self, env: str = None):
        # 读取.env文件获取环境（仅限MYAPP_ENV）
        self.project_path = Path(re.sub('blues_lib.*','',os.path.realpath(__file__)))
        self.env = self._load_environment(env)
        self.system = self._detect_system()
        self.config = self._load_all_configs()
    
    def _load_environment(self, env: str = None) -> str:
        """加载环境设置（仅从.env文件读取MYAPP_ENV）"""
        # 优先级：参数 > 系统环境变量 > .env文件 > 默认值
        if env is not None:
            return env
        
        # 尝试从系统环境变量读取
        if "MYAPP_ENV" in os.environ:
            return os.environ["MYAPP_ENV"]
        
        # 尝试从.env文件读取（仅读取MYAPP_ENV）
        env_file = self.project_path / ".env"
        if env_file.exists():
            with open(env_file,'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key.strip() == "MYAPP_ENV":
                            return value.strip()
        
        return "prod"  # 默认值
    
    def _detect_system(self) -> str:
        """检测当前操作系统"""
        system = platform.system().lower()
        return "macos" if system == "darwin" else system
    
    def _load_all_configs(self) -> Dict[str, Any]:
      """加载并合并所有配置"""

      # base on the sys settings
      package = 'config'

      # 加载基础配置
      config = BluesResource.read_yaml(package, "base.yaml")
      
      # 加载环境特定配置
      env_config = BluesResource.read_yaml(package, f"{self.env}.yaml")
      self._merge_dicts(config, env_config)
      
      # 加载系统特定配置
      system_config = BluesResource.read_yaml(f"{package}.systems", f"{self.system}.yaml")
      self._merge_dicts(config, system_config)
      
      return config
    
    def _merge_dicts(self, base: Dict, update: Dict) -> None:
        """递归合并字典"""
        for k, v in update.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                self._merge_dicts(base[k], v)
            else:
                base[k] = v
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点分隔符）"""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def reload(self) -> None:
        """重新加载配置"""
        self.config = self._load_all_configs()

# 全局配置实例
config = ConfigManager()