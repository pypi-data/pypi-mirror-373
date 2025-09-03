import os
import sys
from base.file import file_util
from base.log import log_util
from base.ninja import ninja_util
from base.tos import tos_util
from base.p4 import p4_util
from business import postcompile_plugin
from business import precompile_plugin
from module.config import product_config
from module.p4 import p4_manager 
from business import compilecachesubmit_plugin
from typing import Union, Dict, List, Callable

class BlazeCache:
    '''
    BlazeCache 最顶层入口类, 封装了底层所有操作
    service 层封装 API 可以直接调用该类
    '''
    
    # 保存所有 product 对应的 product_config.json 存储的 tos 路径
    # _PRODUCT_CONFIG_PATH = {
    #     "lark": "product_config/lark/product_config.json",
    #     "aha-electron": "product_config/aha-electron/product_config.json"
    # }
    
    def __init__(self, product_name: str, build_dir: str, local_repo_dir: Dict,
                 os_type: str, task_type: str, 
                 branch_type: str, machine_id: str, mr_target_branch: Dict, 
                 feature_branch: Dict, p4_client: str, fallback_branch: Dict[str, str], product_tos_path:str, ninja_exe_path: str = None,
                 p4_depot: str = None, p4_stream: str = None, p4_port: str = None):
        self._build_dir = build_dir # 本地代码仓目录
        self._product_name = product_name.lower() # 产品名, 如 lark
        self._os_type = os_type.lower() # 当前运行的操作系统
        self._task_type = task_type.lower() # 当前的任务类型, 一共有两类任务: ci_check_task、cache_generator_task, 对应 product_config.json
        self._branch_type = branch_type.lower() # 分支类型, 一共有两类: main、release
        self._machine_id = machine_id # 机器 id 标识
        
        self._product_tos_path = product_tos_path # 配置文件在 tos 上的存储路径
        
        self._product_config = self._get_product_config()
        
        
        # # 格式化 os_type
        # if self._os_type.startswith("win"):
        #     self._os_type = "Windows"
        # elif self._os_type.startswith('darwin'):
        #     self._os_type = 'Darwin'
        # elif self._os_type.startswith('linux'):
        #     self._os_type = 'Linux'
        self._p4_config = self._product_config.get_p4_config(task_type=self._task_type, branch_type=self._branch_type,
                                                             os_name=self._os_type).to_dict()
        self._p4_config["WORKDIR"] = os.path.join(self._build_dir, self._p4_config["WORKDIR"])
        
        # 这里主要是为了兼容 Lark, Lark 的win堡垒机只能访问 ip 地址, 学清机器只能访问域名
        # 因此提供一个入口, 允许用户自行传入 P4PORT, 如果不传入默认使用配置文件的 P4PORT
        if p4_port is not None:
            self._p4_config["P4PORT"] = p4_port
        
        
        # 判断是否在 sync 后需要删除 client
        self._delete_client = self._p4_config["DELETE_CLIENT"]
        
        self._p4_config["P4CLIENT"] = p4_client
        
        # 对于 lark 这边 release 情况, depot 无法固定在配置文件中, 所以需要上层用户传入参数进行设置
        # 如果用户没有传入, 就默认使用配置文件中设置好的(主干情况)
        self._release_flag = False
        if p4_depot:
            self._release_flag = True
            self._p4_config["P4DEPOT"] = p4_depot
        if p4_stream:
            self._p4_config["P4STREAM"] = p4_stream
        
        self._repo_config = self._product_config.repo_info.repos
        
        # 希望修改的时间戳, 从配置文件获取
        self._target_time_stamp = self._product_config.target_time_stamp
        # 在改戳时需要忽略的目录, 从配置文件获取
        self._time_stamp_exclude_dirs = self._product_config.time_stamp_exclude_dirs
        self._time_stamp_exclude_extensions = self._product_config.time_stamp_exclude_extensions
        
        self._ninja_exe_path = ninja_exe_path # ninja 的可执行程序路径
        
        # 目标合入分支, 结构类似于 {aha: m131, iron: dev}, 用于 cherry-pick 时, 获取开发分支与合入分支最新提交的公共祖先
        self._mr_target_branch = mr_target_branch 
        # 目标合入的 Commit_Id {"aha": xxx, "iron": xxx}, 该参数用于切换分支(CI检查任务用于切换检测分支, 测速任务用于切换编译缓存分支)
        self._feature_branch = feature_branch 
        
        self._ninja_log_path = os.path.join(self._p4_config["WORKDIR"], ".ninja_log") # .ninja_log 文件路径
        self._diff_ninja_log_path = os.path.join(self._p4_config["WORKDIR"], ".diff_ninja_log") # .diff_ninja_log 文件路径
        
        self._logger = log_util.BccacheLogger(name="BlazeCache")
        
        self._local_repo_dir = local_repo_dir # 本地代码仓路径 {"aha": xxx, "iron": xxx}
        
        # 当出现 cherry-pick 冲突失败时, 调用 checkout fallback_branch
        # fallback_branch 格式为: {"aha": "xxx", "iron": "xxx"}
        self._fallback_branch = fallback_branch
        
    def _get_product_config(self):
        base_dir = ""
        if sys.platform.startswith("win"):
            # Windows: %AppData% 对应用户应用数据目录
            base_dir = os.path.expandvars("%AppData%/")
        elif sys.platform.startswith("darwin"):
            # macOS: ~/Library/Application Support/
            base_dir = os.path.expanduser("~/Library/Application Support/")
        elif sys.platform.startswith("linux"):
            # Linux: ~/.config/（注意：正确路径是 ~/.config 而非 ~/./config，两者等价但前者更规范）
            base_dir = os.path.expanduser("~/.config/")
        else:
            # 其他未知系统，默认使用当前目录
            base_dir = os.path.abspath("./") 
        local_product_config_path = os.path.join(base_dir, f"BlazeCache_tmp/product_config/{self._product_name.lower()}/product_config.json")
        
        # product_config 本地若不存在, 则从 tos 中获取
        if not os.path.exists(local_product_config_path):
            file_util.FileUtil.make_directory_exists(os.path.dirname(local_product_config_path))
            remote_product_config_path = self._product_tos_path
            tos_util.BlazeCacheTos.download_file(local_file_path=local_product_config_path, remote_file_path=remote_product_config_path)
        
        config = product_config.ProductConfig(config_path=local_product_config_path)
        # 由于 tos 没有监控文件内容是否改变的功能, 因此想要实现 tos 文件更新时从 tos 下载新文件覆盖本地旧文件比较难实现
        # 所以在每次读取完配置文件以后, 都将本地配置文件删除, 保证每次都从 tos 获取
        os.remove(local_product_config_path)
        
        return config
        
        
    def create_diff_ninja_log(self):
        '''
        编译完成以后, 调用该接口从 .ninja_log 中生成 .diff_ninja_log
        '''
        return postcompile_plugin.PostCompile.create_diff_ninja_log(ninja_log_path=self._ninja_log_path, build_dir=self._p4_config["WORKDIR"],
                                                            ninja_exe_path=self._ninja_exe_path)
    
    def run_precompile_plugin(self, mr_id: str, p4_edit_list: List = [], diff_ninja_log_filter_func: Callable[[str], bool] = None, p4_port: dict = {}):
        '''
        运行 precompile_plugin 入口函数
        
        Args:
            mr_id: 必须传入 mr_id, 用来构建 cherry-pick 成功后的检测分支名
            p4_port: 可选是否传入, 该参数会用于获取所有平台 base_commit 时, 指定连接哪个 P4 Port, dict 结构为 {os_name: p4_port}
        '''
        for repo_dict in self._repo_config:
            for repo_name, repo_config in repo_dict.items():
                repo_config["local_path"] = self._local_repo_dir[repo_name]
                repo_config["mr_target_branch"] = self._mr_target_branch
        
        precompile = precompile_plugin.PreCompile(p4_config=self._p4_config, repo_info=self._repo_config,
                                                  feature_branch=self._feature_branch, delete_client=self._delete_client,
                                                  target_time_stamp=self._target_time_stamp, time_stamp_exclude_dirs=self._time_stamp_exclude_dirs,
                                                  time_stamp_exclude_extensions=self._time_stamp_exclude_extensions,fallback_branch=self._fallback_branch,
                                                  diff_ninja_log_path=self._diff_ninja_log_path, branch_type=self._branch_type, os_type=self._os_type)
        
        depot_name = ""
        if self._release_flag == True:
            depot_name=self._p4_config["P4DEPOT"]
        precompile.run(p4_edit_list=p4_edit_list, diff_ninja_log_filter_func=diff_ninja_log_filter_func, product_config=self._product_config, mr_id=mr_id,
                       depot_name=depot_name, p4_port=p4_port)
        # 执行完以后, 向 .ninja_log 中插入 tag, 标记下一次编译的开始
        ninja = ninja_util.NinjaUtil(build_dir=self._p4_config["WORKDIR"], executable=self._ninja_exe_path)
        ninja.insert_flag_to_ninja_log(self._ninja_log_path)

        
    def run_postcompile_plugin(self):
        '''
        执行完编译后, 生成并获取 .diff_ninja_log
        '''
        self.create_diff_ninja_log()
        return self.get_diff_ninja_log()
    
    
    def run_compile_cache_submit_plugin(self, 
                                     build_executor: Callable[[str], bool],
                                     p4_ignore_url: str, mr_target_branch: Dict[str, str],
                                     p4_submit_label: str,
                                     modify_timestamp: bool = False,
                                     filter_func: Callable[[str], bool] = None,
                                     p4_edit_list: List = []
                                     ) -> bool:  
                                                                                                   
        '''
        运行 compile_cache_submit_plugin 入口函数
        Args:   
            build_workdir (str): 执行编译命令时需要进入的工作目录。
            build_executor (Callable[[str], bool]): 一个用于执行命令的函数。
                                                    它接收一个命令字符串作为参数，返回一个布尔值表示成功或失败。
            p4_ignore_url (str): .p4ignore 文件的下载 URL。
            modify_timestamp: 是否需要修改代码文件时间戳, 默认为 False
        '''
        try:
            # 准备插件所需的 repo_info。
            for repo_dict in self._repo_config:
                for repo_name, repo_config in repo_dict.items():
                    repo_config["local_path"] = self._local_repo_dir[repo_name]
            
            # 如果外部传入 submit_label, 则优先使用外界传入的
            # 需要注意的是, lark 的 release 分支测速任务必须由外界构造好 label 传入
            # 因为 lark 的 release 任务 label 无法固定, 因此无法通过配置文件进行拼接
            if p4_submit_label:
                self._p4_config["SUBMIT_LABEL"] = p4_submit_label
            
            compile_plugin = compilecachesubmit_plugin.CompileCacheSubmit(
                repo_info=self._repo_config,
                mr_target_commit_id=mr_target_branch,
                build_workdir=self._build_dir,
                build_executor=build_executor,
                p4_config=self._p4_config,
                target_time_stamp=self._target_time_stamp,
                time_stamp_exclude_dirs=self._time_stamp_exclude_dirs,
                time_stamp_exclude_extensions=self._time_stamp_exclude_extensions
            )
            
            # 在编译之前, 给.ninja_log添加标记
            ninja = ninja_util.NinjaUtil(build_dir=self._p4_config["WORKDIR"], executable=self._ninja_exe_path)
            ninja.insert_flag_to_ninja_log(self._ninja_log_path)
            
            if not compile_plugin.run_build_phase(modify_timestamp=modify_timestamp):
                self._logger.error("因编译阶段失败，工作流终止。")
                return False
            
            self.create_diff_ninja_log()
            diff_log_path = self.get_diff_ninja_log()
            self._logger.info(f"流程成功完成。差异日志路径: {diff_log_path}")
            if not diff_log_path:
                self._logger.error("因生成或获取差异日志失败，工作流终止。")
                return False
            
            if not compile_plugin.run_submit_phase(diff_ninja_log_path=diff_log_path, p4_ignore_url=p4_ignore_url, filter_func=filter_func,p4_edit_list=p4_edit_list):
                self._logger.error("因缓存提交阶段失败，工作流终止。")
                return False

            self._logger.info("缓存生成与提交全部成功完成！")
            return True
        
        except Exception as e:
            # 捕获任何未预料的异常，确保流程不会崩溃。
            self._logger.error(f"执行 '编译并生成差异日志' 流程时发生未知异常: {e}", exc_info=True)
            return False
    
    
    
        
        
if __name__ == "__main__":
    blaze_cache = BlazeCache(product_name="lark", build_dir="/Users/bytedance/Desktop/lark/src/out/release_apollo_arm64",
                             os_type="dawin", task_type="ci_check_task", branch_type="main",
                             machine_id="1234", ninja_exe_path="/Users/bytedance/Desktop/lark/depot_tools/ninja",
                             mr_target_branch="m131")
    # blaze_cache.create_diff_ninja_log()
    blaze_cache._logger.info(blaze_cache.get_diff_ninja_log())
        