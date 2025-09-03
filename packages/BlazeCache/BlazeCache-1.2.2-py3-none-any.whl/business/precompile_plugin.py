import json
import os
import re
from base.git import git_util
from base.log import log_util
from base.p4 import p4_util
from base.time_stamp import time_stamp_util
from module.p4 import p4_manager
from module.repo import repo_manager
from module.config import product_config
from typing import Union, Dict, List, Callable


class PreCompile:
    '''
    完成编译前的一切准备操作:
    '''
    
    def __init__(self, p4_config: Dict, repo_info: List[Dict], feature_branch: Dict,
                 target_time_stamp: Union[int, float, str], branch_type: str, os_type: str,
                 time_stamp_exclude_dirs: List[str], time_stamp_exclude_extensions: List[str], fallback_branch: Dict[str, str],
                 diff_ninja_log_path: str, delete_client: bool):
        self._logger = log_util.BccacheLogger(name="PreCompile")
        self._p4_config = p4_config
        self._repo_info = repo_info # repo 结构参考 product_config.json
        self._feature_branch = feature_branch # 用户实际修改的 branch, 即用户开发分支
        self._target_time_stamp = target_time_stamp # 希望修改的时间戳
        self._time_stamp_exclude_dirs = time_stamp_exclude_dirs # 需要忽略的改戳目录
        self._time_stamp_exclude_extensions = time_stamp_exclude_extensions # 需要忽略的改戳后缀名
        self._p4 = p4_util.P4Client(self._p4_config) 
        self._time_stamp_util = time_stamp_util.TimeStampUtil(target_time=self._target_time_stamp, exclude_dirs=self._time_stamp_exclude_dirs,
                                                              exclude_extensions=self._time_stamp_exclude_extensions)

        self._p4_label_regex = self._p4_config["LABEL_REGEX"] # 从 p4 label 中提取 commitid 的正则表达式
        
        self._diff_ninja_log_path = diff_ninja_log_path
        self._delete_client = delete_client # 判断 p4 sync 后是否需要删除 client, 由配置文件导入
        
        # 当出现 cherry-pick 冲突失败时, 调用 checkout fallback_branch
        # fallback_branch 格式为: {"aha": "xxx", "iron": "xxx"}
        self._fallback_branch = fallback_branch
        
        self._branch_type = branch_type
        self._os_type = os_type
        
        
    def _init_repo(self):
        '''
        初始化 repo_manager
        '''
        for repo_dict in self._repo_info:
            for repo_name, repo_config in repo_dict.items():
                repo_url = repo_config["url"]
                local_path = repo_config["local_path"]
                repo_config["repo_manager"] = repo_manager.RepoManager(local_path=local_path, repo_url=repo_url)
                repo_config["fallback_branch"] = self._fallback_branch[repo_name]
                
    
    def _get_commit_id_from_label(self, latest_label: str, p4_label_regex) -> Dict:
        '''
        从最近一次提交的 label 中提取 commit_id
        '''
        pattern = p4_label_regex
        matches = re.match(pattern, latest_label)
        if not matches:
            self._logger.error("匹配失败, 请检查正则表达式")
            return None
        result = {}
        for i in range(0, len(matches.groups()), 2):
            if i + 1 < len(matches.groups()):
                repo_name = matches.groups()[i]
                commit_id = matches.groups()[i + 1]
                result[repo_name] = commit_id
        return result
    
    def _get_base_commit_id(self, product_config: product_config.ProductConfig, depot_name: str = "", stream_name: str = "", p4_port: dict = {}):
        '''
        获取基底 commit id, 从所有平台的 p4 服务器 label 中获取, 要求 commit_id 必须所有平台一致
        '''
        # 第四版算法
        os_configs = product_config.os_configs
        label_lists = []
        platfroms = []
        label_regex = []
        
        # 首先动态地获取所有平台的 P4 Config, 提取所有的 label_list, 添加到 label_lists 列表结构中
        for os_name, _ in os_configs.items():
            p4_config = product_config.get_p4_config(task_type="ci_check_task", branch_type=self._branch_type, os_name=os_name).to_dict()
            current_p4_port = None
            if p4_port is not None:
                current_p4_port = p4_port.get(os_name, None)
            if current_p4_port is not None:
                p4_config["P4PORT"] = current_p4_port
            if p4_config["P4PORT"] != "":
                # 创建对应的 p4 client, 获取当前 depot 的 label 列表
                p4_client = p4_util.P4Client(config=p4_config)
                with p4_client as client:
                    labels = client.get_label_lists(depot_name=depot_name, stream_name=stream_name)
                    label_lists.append(labels)
                platfroms.append(os_name)
                label_regex.append(p4_config["LABEL_REGEX"])
        # 如果 label_lists 没有元素, 说明所有平台均为获取 P4 Config, 直接返回 None
        if len(label_lists) == 0:
            self._logger.error("label lists is None, 所有平台均未找到 commit_id")
            return None
        # 如果 label_lists 只有一个元素, 说明只有一个平台的 P4 Config, 直接返回这个平台最新的 commit_id 即可
        # 不需要找公共祖先
        elif len(label_lists) == 1:
            self._logger.info(f"只有一个平台有 commit_id, 直接返回最新一个提交")
            # 先从 label 转换成 commit_id
            # 这里 label_lists 保存的是所有平台的 label 列表, 每个平台的 label 列表保存的是元组结构(label_name, time)
            # 所以这里的结构是 label_lists=[[(label_name, name)]]
            commit_id = self._get_commit_id_from_label(latest_label=label_lists[0][0][0], p4_label_regex=label_regex[0])
            self._logger.info(f'基底 commit_id: {commit_id}')
            label_name = label_lists[0][0][0]
            self._logger.info(f"对应的 p4_label: {label_name}")
            return commit_id, {platfroms[0]: label_name}
        else:
            self._logger.info(f"多个平台有 commit_id, 开始对比, 寻找所有平台的最近公共祖先")
            # 选择 label_lists 的第一个平台作为基底进行比较
            base_label_lists = label_lists[0]
            # base_commit_lists 的结构是 [(label_name, time)]
            for base_index, base_label in enumerate(base_label_lists):
                # 用来判断当前 base_commit 是否在其他所有平台都存在
                base_flag = True
                current_label = {}
                # 首先将需要比较的 label 转换成 commit_id
                base_commit = self._get_commit_id_from_label(latest_label=base_label[0], p4_label_regex=label_regex[0])
                for compare_index, compare_label_lists in enumerate(label_lists[1:], start=1):
                    compare_commit_lists = [self._get_commit_id_from_label(latest_label=compare_label[0], p4_label_regex=label_regex[compare_index]) for compare_label in compare_label_lists]
                    
                    if base_commit not in compare_commit_lists:
                        base_flag = False
                        break
                    else:
                        # 如果当前平台匹配成功, 暂时保存下当前平台的 label
                        current_compare_index = compare_commit_lists.index(base_commit)
                        current_label[platfroms[compare_index]] = compare_label_lists[current_compare_index][0]
                # 如果该条件成立, 说明所有平台均匹配成功, 即找到最近公共祖先, 可以返回结果
                if base_flag == True:
                    self._logger.info(f"找到基底 commit_id: {base_commit}")
                    labels = current_label
                    labels[platfroms[0]] = base_label[0]
                    self._logger.info(f"对应的 label: {labels}")
                    return base_commit, labels
                
        self._logger.error("未找到基底 commit_id")
        return None
        # 第三版算法
        # 逻辑是从 mr_target_branch 的提交列表中, 提取每一个 commit_id, 检测是否所有平台都存在该 commit_id
        
        # 第二版算法, 缺点是极端场景有问题, 且比较难解决
        # 首先获取配置文件的 os_config, 查看配置了多少个平台的 P4 服务器
        # os_configs = product_config.os_configs
        # label_lists = []
        # # 记录 label_lists 的 os_name
        # platfroms = []
        # label_regex = []
        # # 遍历所有平台的 p4_config, 如果配置文件中配置了该平台的 p4_config
        # # 则说明需要查找该平台的 label
        # for os_name, _ in os_configs.items():
        #     p4_config = product_config.get_p4_config(task_type="ci_check_task", branch_type=self._branch_type, os_name=os_name).to_dict()
        #     if p4_config["P4PORT"] != "":
        #         # 创建对应的 p4 client, 获取当前 depot 的 label 列表
        #         p4_client = p4_util.P4Client(config=p4_config)
        #         with p4_client as client:
        #             labels = client.get_label_lists(depot_name=depot_name, stream_name=stream_name)
        #             label_lists.append(labels)
        #         platfroms.append(os_name)
        #         label_regex.append(p4_config["LABEL_REGEX"])

        # # 初始化所有 label_lists 的 index 下标, 默认从 0 位置开始
        # label_indexs = [0] * len(label_lists)
        # while True:
        #     # 如果当其中一个 label_lists 的下标遍历到末尾了, 说明没有找到所有平台的公共祖先 label
        #     # 此时直接返回 None
        #     for i in range(len(label_lists)):
        #         if label_indexs[i] >= len(label_lists[i]):
        #             self._logger.error(f"{platfroms[i]} 的 label 列表已经遍历完了, 仍然没有找到正确的 label, 请检查")
        #             return None
            
        #     # 提取每一个 index 下标对应的 label_lists 元素
        #     # 其中每个 item 就是一个 label, 其结构式一个元组(label_name, time)
        #     current_items = [label_lists[i][label_indexs[i]] for i in range(len(label_lists))]
        #     current_labels = [item[0] for item in current_items]
        #     current_times = [item[1] for item in current_items]

        #     # 将 label 转换成 commit_id
        #     current_commits = [self._get_commit_id_from_label(latest_label=label, p4_label_regex=label_regex[i]) for i, label in enumerate(current_labels)]
        #     if all(commit == current_commits[0] for commit in current_commits):
        #         self._logger.info(f"成功找到所有平台均一致的最新的 commit_id: {current_commits[0]}")
        #         base_commit_labels = {}
        #         for i in range(len(platfroms)):
        #             base_commit_labels[platfroms[i]] = current_labels[i]
        #         self._logger.info(f"base_commit_labels: {base_commit_labels}")
        #         return current_commits[0], base_commit_labels
            
        #     # 找到当前时间最小的那个元素的索引（可能有多个，取第一个）
        #     min_time = min(current_times)
        #     min_time_index = [i for i, j in enumerate(current_times) if j == min_time]

        #     # 除了时间最小的那个列表，其他列表的下标都+1（查看更旧的元素）
        #     for i in range(len(label_indexs)):
        #         if i not in min_time_index:
        #             label_indexs[i] += 1

        # 第一版算法, 缺点是不够动态灵活
        # mac_p4_config = product_config.get_p4_config(task_type="ci_check_task", branch_type=self._branch_type, os_name="Darwin").to_dict()
        # win_p4_config = product_config.get_p4_config(task_type="ci_check_task", branch_type=self._branch_type, os_name="Windows").to_dict()
        # linux_p4_config = product_config.get_p4_config(task_type="ci_check_task", branch_type=self._branch_type, os_name="Linux").to_dict()
        # mac_p4_labels = []
        # win_p4_labels = []
        # linux_p4_labels = []
        # mac_commits = []
        # win_commits = []
        # linux_commits = []
        # # 并不一定是所有平台都会部署 P4, 因此没有部署 P4 的平台, 对应配置文件的 P4PORT 一定是空字符串
        # # 只有成功获取到 P4PORT 才会去连接 P4 服务器
        # if mac_p4_config["P4PORT"] != "":
        #     p4_client = p4_util.P4Client(config=mac_p4_config)
        #     with p4_client as client:
        #         # 连接上服务器后, 获取指定 depot&stream 的 label 列表, 这里会按更新时间降序排序
        #         # 这里的 depot_name&stream_name, 如果是主干, 则从配置文件里获取, 对应的参数传递空字符串即可, 默认从配置文件加载
        #         # 如果是 release 分支, 由于 depot_name 不固定, 无法写入配置文件, 需要通过参数传递
        #         mac_p4_labels = client.get_label_lists(depot_name=depot_name, stream_name=stream_name)
        #         # 遍历获取到的 label 列表, 将所有 label 进行转换, 提取出 commit_id
        #         for label in mac_p4_labels:
        #             commit = self._get_commit_id_from_label(latest_label=label[0], p4_label_regex=mac_p4_config["LABEL_REGEX"])
        #             mac_commits.append(json.dumps(commit))
                    
        # if win_p4_config["P4PORT"] != "":
        #     p4_client = p4_util.P4Client(config=win_p4_config)
        #     with p4_client as client:
        #         win_p4_labels = client.get_label_lists(depot_name=depot_name, stream_name=stream_name)
        #         for label in win_p4_labels:
        #             commit = self._get_commit_id_from_label(latest_label=label[0], p4_label_regex=win_p4_config["LABEL_REGEX"])
        #             win_commits.append(json.dumps(commit))
                    
        # if linux_p4_config["P4PORT"] != "":
        #     p4_client = p4_util.P4Client(config=linux_p4_config)
        #     with p4_client as client:
        #         linux_p4_labels = client.get_label_lists(depot_name=depot_name, stream_name=stream_name)
        #         for label in linux_p4_labels:
        #             commit = self._get_commit_id_from_label(latest_label=label[0], p4_label_regex=linux_p4_config["LABEL_REGEX"])
        #             linux_commits.append(json.dumps(commit))

        # # 保存所有的非空列表, 以适配所有的场景, 比如 Lark 只有 Mac 和 Win 平台
        # # 比如 clickhouse 只有 Linux 平台
        # non_empty_commits = []
        # if mac_commits:
        #     # 这里将 commits 列表和对应的 labels 列表都保存起来, 它们的顺序是一致的
        #     # 这样做的目的是将来找到所有平台都存在的 commit 后, 能直接提取出其对应的 label
        #     non_empty_commits.append({"commit_lists": mac_commits, "label_lists": mac_p4_labels, "os": "Darwin"})
        # if win_commits:
        #     non_empty_commits.append({"commit_lists": win_commits, "label_lists": win_p4_labels, "os": "Windows"})
        # if linux_commits:
        #     non_empty_commits.append({"commit_lists": linux_commits, "label_lists": linux_p4_labels, "os": "Linux"})

        # if len(non_empty_commits) == 0:
        #     self._logger.error("non_empty_commits is None, 未找到基底 commit_id")
        #     return None
        # elif len(non_empty_commits) == 1:
        #     self._logger.info(f"只有一个平台有 commit_id, 直接返回最新一个提交")
        #     self._logger.info(f'基底 commit_id: {non_empty_commits[0]["commit_lists"][0]}')
        #     labels = {non_empty_commits[0]["os"]: non_empty_commits[0]["label_lists"][0][0]}
        #     self._logger.info(f"对应的 p4_label: {labels}")
        #     return json.loads(non_empty_commits[0]["commit_lists"][0]), labels
        # else:
        #     self._logger.info(f"多个平台有 commit_id, 开始对比")
        #     base_commit_lists = non_empty_commits[0]
        #     labels = {}
        #     for index, base_commit in enumerate(base_commit_lists["commit_lists"]):
        #         # 用来判断当前 base_commit 是否在其他所有平台都存在
        #         base_flag = True
        #         current_label = {}
        #         for commit_lists in non_empty_commits[1:]:
        #             # 如果 base_commit 不在 commit_lists 中, 说明当前 base_commit 不是在所有平台都有的 commit,直接break
        #             if base_commit not in commit_lists["commit_lists"]:
        #                 base_flag = False
        #                 break
        #             else:
        #                 # 这里需要提取出 base_commit 在 commit_lists 中的索引, 然后根据索引提取出对应的 label
        #                 # 注意不能用最外层的 index 作为下标, 因为最外层的 index 是 base_commit_lists 的索引, index 在 commit_lists 中不一定能对应上
        #                 commit_index = commit_lists["commit_lists"].index(base_commit)
        #                 current_label[commit_lists["os"]] = commit_lists["label_lists"][commit_index][0]
        #         if base_flag == True:
        #             self._logger.info(f"找到基底 commit_id: {base_commit}")
        #             labels = current_label
        #             labels[base_commit_lists["os"]] = base_commit_lists["label_lists"][index][0]
        #             self._logger.info(f"对应的 label: {labels}")
        #             return json.loads(base_commit), labels
                
        # self._logger.error("未找到基底 commit_id")
        # return None
        
    
    def run(self, product_config: product_config.ProductConfig, mr_id: str, p4_edit_list: List = [], diff_ninja_log_filter_func: Callable[[str], bool] = None, depot_name: str = "", stream_name: str = "",
            p4_port: dict = {}):
        '''
        运行入口函数
        '''        
        self._init_repo()
        # 获取基底的 commit_id
        # 这里有个坑, self._p4 客户端在此处第一次建立连接, 断开连接以后会销毁对象
        # 所以后面 p4_manager 复用这里的 p4 client 会连接失败
        # 但之前 p4_manager 连接失败时, 其实并没有受太大影响, 还是能正常运行所有 p4 流程
        # 这是由于 p4 会保留连接会话, 并非立即销毁, 但当第一次连接和第二次连接之间跨越很长时间时
        # 会话过期了, p4 操作就会全部失效, 因此这里不能复用同一个 p4 client 对象
        
        base_commit_id, labels = self._get_base_commit_id(product_config=product_config, depot_name=depot_name, stream_name=stream_name, p4_port=p4_port)
        label_name = labels.get(self._os_type, "")
        self._logger.info(f"提取到的 label_name: {label_name}")
        
        for repo_dict in self._repo_info:
            for repo_name, repo_config in repo_dict.items():
                # 切换基底 commit_id
                repo_config["repo_manager"].CheckoutRepo(branch=base_commit_id[repo_name], 
                                                         git_clean_excludes=repo_config["git_clean_excludes"])
                # 改代码时间戳
                self._time_stamp_util.process_directory(root_dir=repo_config["local_path"])
                
                # 从用户的 feature 分支获取用户新增的 commitId
                git_operator = git_util.GitOperator(repo_path=repo_config["local_path"])
                # 这里的 target_branch 需要使用合入分支最新提交, 不能使用基底 commit
                feature_commit_id = git_operator.get_commits_lists(target_branch=repo_config["mr_target_branch"][repo_name], feature_branch=self._feature_branch[repo_name])
                cherry_pick_success = True
                for commit_id in feature_commit_id:
                    if commit_id is not None:
                        # 如果 cherry-pick 失败, 可能是出现了冲突, 直接无脑调用 checkout fallback_branch
                        if git_operator._run_command(command_args=["cherry-pick", commit_id]) is None:
                            git_operator._run_command(command_args=["cherry-pick", "--abort"])
                            fallback_branch = repo_config["fallback_branch"]
                            git_operator.checkout_branch(branch=fallback_branch)
                            cherry_pick_success = False
                            break
                # 如果 cherry-pick 成功, 需要将其 push 到远端分支, 方便后续排查
                if cherry_pick_success == True:
                    remote_name = git_operator._get_primary_remote()
                    branch_name = f"blazecache_verify/mr-{mr_id}"
                    git_operator._run_command(["push", remote_name, f"HEAD:refs/heads/{branch_name}"])
                        
        
        
        # 执行 p4 拉缓存操作
        p4 = p4_util.P4Client(config=self._p4_config)
        manager = p4_manager.P4Manager(p4_client=p4)
        manager.run_ci_check_task(diff_ninja_log_file=self._diff_ninja_log_path, delete_client=self._delete_client, filter_func=diff_ninja_log_filter_func, p4_edit_list=p4_edit_list,
                                  label_name=label_name)
        self._logger.info(f"拉取缓存结束, 可以执行编译了")
        