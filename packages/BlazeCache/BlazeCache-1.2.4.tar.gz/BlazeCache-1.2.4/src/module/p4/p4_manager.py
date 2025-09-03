import os
from base.file import file_util
from base.log import log_util
from base.p4 import p4_util
from typing import Callable, List


class P4Manager:
    
    def __init__(self, p4_client: p4_util.P4Client):
        self._p4_client = p4_client
        self._logger = log_util.BccacheLogger(name="P4Manager")
    
    def get_diffs(self, diff_ninja_log_file: str, filter_func: Callable[[str], bool] = None) -> List:
        '''
        从 .diff_ninja_log 中获取 diffs 文件列表
        
        Args: 
            diff_ninja_log_file: .diff_ninja_log 文件路径
            filter_func: 筛选函数, 提供入口给用户自定义筛选逻辑, 传入 .diff_ninja_log 中的 target name, 将符合条件的 target 保留
            使用示例, 参考 Lark:
            def lark_filter(name):
                if name.split(".")[-1] in ["stamp", "o", "obj", "lib", "h", "res", "exe", "cc", "pdb", "dll" ,'a' ,'unstripped' ,'dylib' ,'TOC']:
                    if name not in  ["frame.dll.pdb","frame.dll","frame.dll.lib"]:
                        return True

                    # 检查是否为无后缀的 Unix/macOS 可执行文件
                    if os.path.isfile(os.path.join(code_dir, 'out/{}/{}'.format(output_dir_name,name.replace('.unstripped','')))):
                        return True

                elif name.endswith("ids"): #gen/tools/gritsettings/default_resource_ids should be taken in account
                    return True
                else:
                    return False
            
        Returns:
            返回筛选完后的 diff file lists
        '''
        if not diff_ninja_log_file:
            self._logger.info(f"diff_ninja_log_file is None: {diff_ninja_log_file}")
            return []
        try:
            diff_file_lists = []
            with open(diff_ninja_log_file, 'r') as log:
                for line in log:
                    parts = line.strip().split('\t')
                    if len(parts) != 5:
                        # If ninja.exe is rudely halted then the .ninja_log file may be
                        # corrupt. Silently continue.
                        continue
                    _, _, _, name, _ = parts # Ignore restat.
                    if filter_func is None or filter_func(name):
                        diff_file_lists.append(name)
                
            return diff_file_lists
        except IOError as e:
            self._logger.info(f"get_diffs error {e}")
        
       
    def run_cache_generator_task(self, p4_ignore_url: str, diff_ninja_log_file: str, filter_func: Callable[[str], bool] = None,p4_edit_list: List = []):
        '''
        封装测速任务 P4 执行逻辑
        
        Agrs:
            p4_ignore_url: 下载 .p4ignore 文件的 url 
            diff_ninja_log_file: .diff_ninja_log 文件路径
        '''
        with self._p4_client as client:
            # 首先查看服务器是否已经存在 depot, 如果不存在, 说明是首次上传缓存
            if not client.check_depot():
                self._logger.info(f"depot {client.depot} 不存在, 第一次上传缓存")
                client.create_depot(depot_type="stream")
                self._logger.info(f"create stream {client.stream}")
                client.create_stream()
                self._logger.info(f"create client {client.client}")
                client.create_client(options=["allwrite", "clobber"])
                
                # 由于是首次上传 P4 缓存, 所以需要下载 .p4ignore 并上传
                file_util.FileUtil.download_url(p4_ignore_url, f"{client.work_dir}/.p4ignore")
                self._logger.info(f"p4 add -t -mwx .p4ignore")
                client.add_file(filespecs=[".p4ignore"], options=["-t", "+mwx"])
                self._logger.info(f"p4 submit .p4ignore")
                client.submit(filespecs=[".p4ignore"], options=["-d", "submit .p4ignore"])
                
                # 上传全量缓存
                self._logger.info(f"p4 add -f -t binary+mwx ...")
                client.add_file(filespecs=["..."], options=["-f", "-t", "binary+mwx"])
                self._logger.info(f"p4 submit ... -d {client.submit_label}")
                client.submit(filespecs=["..."], options=["-d", client.submit_label])
                self._logger.info(f"create label")
                client.create_label(client.submit_label)
                self._logger.info(f"labelsync -l {client.submit_label} //{client.depot}/{client.stream}...")
                client.labelsync(filespecs=[f"//{client.depot}/{client.stream}..."], options=["-l", client.submit_label])
                
            else:
                self._logger.info(f"depot {client.depot} 已存在, 增量上传缓存")
                self._logger.info(f"create client {client.client}")
                client.create_client(options=["allwrite", "clobber"])
                self._logger.info(f"p4 add -t binary+mwx ...")
                client.add_file(filespecs=["..."], options=["-t", "binary+mwx"])
                self._logger.info(f"p4 reconcile -d -e -m ...")
                client.reconcile(filespecs=["..."], options=["-d", "-e", "-m"])
                diff_file_lists = self.get_diffs(diff_ninja_log_file=diff_ninja_log_file, filter_func=filter_func)
                default_changelists = client.get_opened_files(options=["-c", "default"])
                
                # 剔除掉 .diff_ninja_log 中已经加入到 changelist 的文件, 以防止后续冗余 edit, 从而减少耗时
                diff_file_lists.extend(p4_edit_list)
                diff_file_lists = [item for item in diff_file_lists if item not in default_changelists]
                
                self._logger.info(f"p4 edit -f")
                client.edit_files(diff_file_lists)
                self._logger.info(f"p4 submit -d {client.submit_label} ...")
                client.submit(filespecs=["..."], options=["-d", client.submit_label])
                self._logger.info(f"create label {client.submit_label}")
                client.create_label(client.submit_label)
                self._logger.info(f"p4 labelsync -l {client.submit_label} //{client.depot}/{client.stream}...")
                client.labelsync(filespecs=[f"//{client.depot}/{client.stream}..."], options=["-l", client.submit_label])
    
    def run_ci_check_task(self, diff_ninja_log_file: str, label_name:str, delete_client: bool = True, filter_func: Callable[[str], bool] = None, p4_edit_list: List = []):
        '''
        封装 CI 检查编译前 Perforce 的工作流程
        
        Args:
            diff_ninja_log_file: .diff_ninja_log 的文件路径
        '''
        with self._p4_client as client:
            if client.check_client(client_name=client.client):
                self._logger.info(f"client {client.client} 已存在, 增量拉取缓存")
                
                self._logger.info(f"执行 p4 reconcile -a -d -e -m")
                client.reconcile(filespecs=["..."], options=["-a", "-d", "-e", "-m"])
                
                default_changelists = client.get_opened_files(options=["-c", "default"])
                self._logger.info(f"从 p4 reconcile 获取的文件数量: {len(default_changelists)}")
                
                diff_file_lists = self.get_diffs(diff_ninja_log_file=diff_ninja_log_file, filter_func=filter_func)
                self._logger.info(f"从 .diff_ninja_log 中获取的文件数量: {len(diff_file_lists)}")
                
                diff_file_lists = [item for item in diff_file_lists if item not in default_changelists]
                self._logger.info(f"从 .diff_ninja_log - p4 reconcile 的文件数量: {len(diff_file_lists)}")
                
                p4_edit_list.extend(diff_file_lists)
                self._logger.info(f"最终交给 p4 edit 的文件数量: {len(p4_edit_list)}")
                
                self._logger.info(f"执行 p4 edit -f")
                client.edit_files(file_list=diff_file_lists)
                
                opened_file_lists = client.get_opened_files(options=["-c", "default"])
                self._logger.info(f"即将 revert 文件数量: {len(opened_file_lists)}")
                
                self._logger.info(f"执行 p4 revert")
                client.revert(filespecs=[f"//{client.depot}/{client.stream}..."])
                self._logger.info(f"p4_label: {label_name}")
                self._logger.info(f"执行 p4 sync")
                client.sync(filespecs=[f"//{client.depot}/{client.stream}/...@{label_name}"])
            else:
                self._logger.info(f"client {client.client} 不存在, 全量拉取缓存")
                client.create_client(options=["allwrite", "clobber"])
                self._logger.info(f"p4_label: {label_name}")
                self._logger.info(f"执行 p4 sync -f")
                client.sync(filespecs=[f"//{client.depot}/{client.stream}/...@{label_name}"], options=["-f"])
                if delete_client:
                    self._logger.info(f"执行 p4 client -d")
                    client.delete_client()

if __name__ == "__main__":
    p4_config = {
        "P4PORT": "10.92.102.157:1666",
        "P4USER": "native_win",
        "P4CLIENT": "test-ci-check",
        "P4PASSWD": "Bdeefe-1",
        "DEPOT": "test-bccache",
        "STREAM": "main",
        "SUBMIT_LABEL": "aha_354bffd64404f90014438b1271127f2eb5c2994b_iron_9c3987477ed61005f0327f2cdbf345772ffd4f62",
        "WORKDIR": "/Users/bytedance/Desktop/lark/src/out/release_apollo_arm64"
    }
    
    p4_maneger = P4Manager(p4_config=p4_config)
    # p4_maneger.run_cache_generator_task(p4_ignore_url="https://voffline.byted.org/download/tos/schedule/mybucket/self_signed_cache/bits/mac/.p4ignore", diff_ninja_log_file="/Users/bytedance/Desktop/lark/src/out/release_apollo_arm64/.diff_ninja_log")
    p4_maneger.run_ci_check_task(diff_ninja_log_file="/Users/bytedance/Desktop/lark/src/out/release_apollo_arm64/.diff_ninja_log")      
            