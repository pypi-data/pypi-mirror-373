import os
import json
from base.log import log_util
from typing import Dict, Optional, Any, List

logger = log_util.BccacheLogger(name="ProductConfig")

class P4Config:
    """Perforce 配置类，存储单个 P4 服务器的连接信息"""
    
    def __init__(self, data: Dict[str, str]):
        self.P4PORT = data.get("P4PORT", "")
        self.P4USER = data.get("P4USER", "")
        self.P4DEPOT = data.get("P4DEPOT", "")
        self.P4STREAM = data.get("P4STREAM", "")
        self.P4PASSWD = data.get("P4PASSWD", "")
        self.WORKDIR = data.get("WORKDIR", "")
        self.LABEL_REGEX = data.get("LABEL_REGEX", "")
        self.SUBMIT_LABEL = data.get("SUBMIT_LABEL", "")
        self.DELETE_CLIENT = data.get("DELETE_CLIENT", "")
        
    def to_dict(self) -> Dict[str, str]:
        return {
            "P4PORT": self.P4PORT,
            "P4USER": self.P4USER,
            "P4DEPOT": self.P4DEPOT,
            "P4STREAM": self.P4STREAM,
            "P4PASSWD": self.P4PASSWD,
            "WORKDIR": self.WORKDIR,
            "LABEL_REGEX": self.LABEL_REGEX,
            "SUBMIT_LABEL": self.SUBMIT_LABEL,
            "DELETE_CLIENT": self.DELETE_CLIENT
        }

class TaskConfig:
    """任务配置类，包含 main 和 release 两种环境的 P4 配置"""
    
    def __init__(self, data: Dict[str, Dict[str, str]]):
        for branch_name, branch_config in data.items():
            setattr(self, branch_name, P4Config(branch_config))

class OSConfig:
    """操作系统配置类，包含不同任务类型的配置"""
    
    def __init__(self, data: Dict[str, Dict[str, Dict[str, str]]]):
        for os_name, os_config in data.items():
            setattr(self, os_name.lower(), TaskConfig(os_config))

class RepoInfo:
    """仓库信息类，包含多个仓库的 URL"""
    
    def __init__(self, data: List[Dict[str, Dict[str, str]]]):
        self.repos = []
        for repo in data:
            repo_dict = {}
            for repo_name, repo_config in repo.items():
                repo_info = {}
                repo_info["url"] = repo_config.get("url", "")
                repo_info["git_clean_excludes"] = repo_config.get("git_clean_excludes", [])
                repo_dict[repo_name] = repo_info
            self.repos.append(repo_dict)
                
    

class ProductConfig:
    """配置文件主类，解析并管理整个配置结构"""
    
    # @staticmethod
    # def get_current_os() -> str:
    #     """获取当前操作系统名称，映射为配置文件中的键"""
    #     platform = os.sys.platform
    #     logger.info(f"os: {platform}")
    #     if platform.startswith('win'):
    #         return 'windows'
    #     elif platform.startswith('darwin'):
    #         return 'darwin'
    #     elif platform.startswith('linux'):
    #         return 'linux'
    #     return platform  # 未知系统
    
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.product_name = data.get("product_name", "")
        self.target_time_stamp = data.get("target_time_stamp", "")
        self.time_stamp_exclude_dirs = data.get("time_stamp_exclude_dirs", [])
        self.time_stamp_exclude_extensions = data.get("time_stamp_exclude_extensions", [])
        self.repo_info = RepoInfo(data.get("repo_info", []))
        
        # 解析不通操作系统下的 P4 配置
        self.os_configs = {}
        for os_name, os_data in data.get("p4_config", {}).items():
            self.os_configs[os_name.lower()] = OSConfig(os_data)
    
    def get_os_config(self, os_name: Optional[str] = None) -> Optional[OSConfig]:
        """
        获取指定操作系统的配置，默认为当前操作系统
        
        Args:
            os_name: 指定要获取的 p4 config 对应操作系统
        """
        # os_name = os_name or self.get_current_os()
        return self.os_configs.get(os_name)
    
    def get_p4_config(self, task_type: str, branch_type: str, os_name: Optional[str] = None) -> Optional[P4Config]:
        """
        获取特定任务类型和环境类型的 P4 配置
        
        Args:
            task_type: 任务类型，如 "ci_check_task" 或 "cache_generator_task"
            branch_type: 分支类型，如 "main" 或 "release"
            os_name: 操作系统名称，默认为当前操作系统
        """
        os_config = self.get_os_config(os_name)
        if not os_config:
            return None
            
        task_config = getattr(os_config, task_type, None)
        if not task_config:
            return None
            
        return getattr(task_config, branch_type, None)
