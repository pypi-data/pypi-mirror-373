import os
import re
from base.log import log_util
from base.p4 import p4_util
from base.time_stamp import time_stamp_util
from module.p4 import p4_manager
from module.repo import repo_manager
from typing import Union, Dict, List, Callable
from base.file import file_util
from business import postcompile_plugin


class CompileCacheSubmit:
    """
    一个用于执行编译并提交缓存的插件。
    此插件的核心任务是：
    1. 准备代码工作区，切换到指定的用户 commit。
    2. 执行用户提供的编译命令。
    3. 将缓存提交到持久化存储（P4）。
    """

    def __init__(self, repo_info: List[Dict], 
                 mr_target_commit_id: Dict, 
                 build_workdir: str,
                 build_executor: Callable[[str], bool],
                 p4_config: Dict,
                 target_time_stamp: Union[int, float, str],
                 time_stamp_exclude_dirs: List[str], time_stamp_exclude_extensions: List[str],
                 code_init_func: Callable[[str], None] = None):
        """
        初始化插件。

        Args:
            repo_info (List[Dict]): 一个列表，包含了所有代码仓库的信息。
                                     结构: [{"repo_name": {"url": "...", "local_path": "..."}}, ...]
            mr_target_commit_id (Dict): 一个字典，映射了仓库名到用户想要编译的目标 commit ID。
                                        结构: {"repo_name": "commit_id_string", ...}
            build_workdir (str): 执行编译命令时需要进入的工作目录。
            build_executor (Callable[[str], bool]): 一个用于执行命令的函数。
                                                    它接收一个命令字符串作为参数，返回一个布尔值表示成功或失败。   
            p4_config (Dict): Perforce 的完整配置字典。                                                    
            code_init_func (Callable, optional): 一个可选的回调函数，在代码 checkout 后执行。默认为 None。
        """
        self._logger = log_util.BccacheLogger(name="CompileCacheSubmitPlugin")
        self._repo_info = repo_info
        self._mr_target_commit_id = mr_target_commit_id
        self._code_init_func = code_init_func

        # 编译相关配置
        self._build_workdir = build_workdir
        self._build_executor = build_executor # 执行编译
          
        #内部实例化 P4 管理器
        self._p4_config = p4_config
        self._p4_client = p4_util.P4Client(self._p4_config)
        self._p4_manager = p4_manager.P4Manager(self._p4_client) 
        
        # 初始化所有代码仓库的管理器
        self._init_repo_managers()     
        self._logger.info("编译提缓存插件初始化完成。")
        
        self._target_time_stamp = target_time_stamp # 希望修改的时间戳
        self._time_stamp_exclude_dirs = time_stamp_exclude_dirs # 需要忽略的改戳目录
        self._time_stamp_exclude_extensions = time_stamp_exclude_extensions # 需要忽略的改戳后缀名
        self._time_stamp_util = time_stamp_util.TimeStampUtil(target_time=self._target_time_stamp, exclude_dirs=self._time_stamp_exclude_dirs,
                                                              exclude_extensions=self._time_stamp_exclude_extensions)

    def _init_repo_managers(self):
        """
        遍历 repo_info，为每个代码仓库创建并初始化一个 RepoManager 实例。
        """
        self._logger.info("正在初始化代码仓库管理器...")
        for repo_dict in self._repo_info:
            for repo_name, repo_config in repo_dict.items():
                if "repo_manager" not in repo_config:
                    repo_url = repo_config["url"]
                    local_path = repo_config["local_path"]
                    repo_config["repo_manager"] = repo_manager.RepoManager(local_path=local_path, repo_url=repo_url)
                    self._logger.info(f"仓库 '{repo_name}' 的管理器已创建。")

    def checkout_target_commit(self):
        """
        一：进入每个代码仓库，并切换到用户指定的目标 commit ID。
        """
        self._logger.info("开始切换代码仓库到目标 commit...")
        if not self._mr_target_commit_id:
            self._logger.error("目标 commit ID (_mr_target_commit_id) 为空，无法切换代码。")
            raise ValueError("Cannot check out code with an empty target commit ID map.")

        for repo_dict in self._repo_info:
            for repo_name, repo_config in repo_dict.items():
                if repo_name not in self._mr_target_commit_id:
                    self._logger.warning(f"在目标 commit 字典中未找到仓库 '{repo_name}' 的 commit ID，将跳过此仓库。")
                    continue

                target_commit = self._mr_target_commit_id[repo_name]
                repo_manager = repo_config["repo_manager"]

                self._logger.info(f"正在将仓库 '{repo_name}' 切换到 commit: {target_commit}")
                try:
                    # 调用 RepoManager 的方法来执行实际的 git/p4 checkout 操作
                    # clean=False, shallow=False 表明是在一个已存在的工作区上更新，而不是全新克隆
                    repo_manager.CheckoutRepo(branch=target_commit, git_clean_excludes=repo_config["git_clean_excludes"])
                    self._logger.info(f"仓库 '{repo_name}' 已成功切换。")
                except Exception as e:
                    self._logger.error(f"切换仓库 '{repo_name}' 到 commit '{target_commit}' 时失败: {e}")
                    raise RuntimeError(f"无法切换仓库 '{repo_name}' 到目标commit: {e}") from e

        self._logger.info("所有代码仓库均已切换到指定 commit。代码准备阶段完成。")

    def execute_build(self) -> bool:
        """
        二：在指定的工作目录下，使用注入的执行器函数来运行编译命令。
        """
        self._logger.info(f"准备执行编译...")
        self._logger.info(f"工作目录: {self._build_workdir}")

        if not os.path.exists(self._build_workdir):
            self._logger.error(f"编译工作目录不存在: {self._build_workdir}")
            return False

        try:
            # 使用您提供的 ChangeDirectory 上下文管理器来确保我们处于正确的目录
            with file_util.ChangeDirectory(self._build_workdir):
                self._logger.info(f"已进入工作目录: {os.getcwd()}")
                
                # 调用外部注入的编译执行器函数
                build_success = self._build_executor()

            if build_success:
                self._logger.info("编译命令执行成功。")
            else:
                self._logger.error("编译命令执行失败。请检查日志。")
            
            return build_success

        except Exception as e:
            self._logger.error(f"执行编译时发生意外错误: {e}")
            return False
  
    def run_build_phase(self, modify_timestamp: bool = False) -> bool:
        """
        插件第一阶段主执行函数。
        """
        try:
            # 步骤一：准备代码
            self.checkout_target_commit()
            if modify_timestamp == True:
                for repo_dict in self._repo_info:
                    for _, repo_config in repo_dict.items():
                        self._time_stamp_util.process_directory(root_dir=repo_config["local_path"])

            # 步骤二：执行编译
            if not self.execute_build():
                # 如果编译失败，则提前终止整个流程
                self._logger.error("由于编译失败，插件执行终止。")
                return False
         
            
            return True
        except Exception as e:
            self._logger.error(f"插件执行过程中发生严重错误: {e}")
            return False
        
    def run_submit_phase(self, diff_ninja_log_path: str, p4_ignore_url: str, filter_func: Callable[[str], bool] = None,p4_edit_list: List = []) -> bool:
        """
        插件第二阶段运行函数：提交缓存到 Perforce。

        Args:
            diff_ninja_log_path (str): .diff_ninja_log 文件的本地路径。
            p4_ignore_url (str): .p4ignore 文件的下载 URL。
        
        Returns:
            bool: 提交成功返回 True, 否则返回 False。
        """
        self._logger.info("开始执行插件的 [缓存提交阶段]...")
        if not diff_ninja_log_path or not os.path.exists(diff_ninja_log_path):
            self._logger.error(f"提供的 diff_ninja_log 路径无效或文件不存在: '{diff_ninja_log_path}'")
            return False
            
        try:
            # 调用注入的 P4Manager 来执行任务
            self._p4_manager.run_cache_generator_task(
                p4_ignore_url=p4_ignore_url,
                diff_ninja_log_file=diff_ninja_log_path,
                filter_func=filter_func,
                p4_edit_list = p4_edit_list
            )
            self._logger.info("[缓存提交阶段] 成功完成。")
            return True
        except Exception as e:
            self._logger.error(f"[缓存提交阶段] 发生严重错误: {e}", exc_info=True)
            return False