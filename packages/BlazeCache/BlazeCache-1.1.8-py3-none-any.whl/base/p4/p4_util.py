# p4utils.py
"""
P4工具类，用于封装Perforce客户端常用操作
"""
import datetime
import os
import sys
import tempfile
from base.log import log_util
from typing import List, Dict, Any
from P4 import P4, P4Exception


class P4Client:
    """
    用于封装 p4 client 常用方法，包括：
        1. 获取 p4 config, 为了不让 init 函数参数列表过长, 采用 Dict 方式传入 config 参数
        2. 获取 p4 connection 建立与服务器连接
        3. p4 client、depot、label、stream 相关操作（增删改查）
        4. p4 reconcile、edit、revert、sync、submit 等相关操作
    """
    
    # 互斥选项映射（键为新选项，值为应移除的旧选项）
    # 由于 client 有 Options 选项, 如果用户需要修改, 参考 create_client 函数
    _CLIENT_MUTUALLY_EXCLUSIVE = {
        "allwrite": "noallwrite",
        "clobber": "noclobber",
        "compress": "nocompress",
        "altsync": "noaltsync",
        "modtime": "nomodtime",
        "rmdir": "normdir"
    }
    
    # 列举 Client 的所有 line ending type
    # Client 默认为 local
    _CLIENT_LINE_ENDING_TYPE = [
        "local",
        "unix",
        "mac",
        "win",
        "shared"
    ]
    
    def __init__(self, config: Dict = None):
        self.p4 = P4()
        self.config = config or {}
        
        self.logger = log_util.BccacheLogger(
            name="P4Client",
            use_console=True
        )
        
        # 配置连接参数
        self.p4.port = self.config.get('P4PORT', 'localhost:1666')
        self.p4.user = self.config.get('P4USER', 'perforce')
        self.p4.client = self.config.get('P4CLIENT', f"{self.p4.user}_client")
        self.p4.password = self.config.get('P4PASSWD')
        self._depot = self.config.get('P4DEPOT')
        self._stream = self.config.get('P4STREAM')
        self._sync_label = self.config.get('SYNC_LABEL')
        self._submit_label = self.config.get('SUBMIT_LABEL')
        self._work_dir = self.config.get('WORKDIR', None)
        
        # 必须设置 Perforce 的工作目录, 后续所有操作均在工作目录下进行
        if self.work_dir is None:
            raise ValueError("Perforce 工作目录未设置")
        self.p4.cwd = self.work_dir
    
    def connect(self) -> bool:
        """
        建立与 Perforce 服务器的连接，需要在对象初始化后被调用
        确保连接建立后再执行 P4 操作
        """
        try:
            self.logger.info(f"Connecting to {self.p4.port} as {self.p4.user}")
            self.p4.connect()
            if self.p4.password:
                self.p4.run_login()
            self.logger.info(f"Connection successful: {self.p4.run_info()}")
            return True
        except P4Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            return False
    
    def create_client(self, client_name: str = "", options: List[str] = [], line_ending_type: str = "") -> bool:
        """
        封装 P4 创建工作区 client 函数
        创建工作区流程：
            1. 获取 client 规范输出
            2. 修改 client 规范输出, 填充自定义 client 信息
            3. 创建 client
        Args:
            options: 可选参数列表, 用于修改 client 的 Options
            默认为 ["noallwrite noclobber nocompress unlocked nomodtime normdir"]
            line_ending_type: 文件格式类型, 默认为 local, 具体类型参考 CLIENT_LINE_ENDING_TYPE 或 p4 官方文档
        """
        try:
            if not client_name:
                client_name = self.p4.client
            
            client_spec = self.p4.fetch_client(client_name)
            
            # 设置流式 client, 这里必须指定流
            # 否则就需要 Client 里指定 View 视图
            # 非流式 Client 默认的 Client View 视图不可用于 Stream Depot
            stream_name = None
            if self.stream and not self.stream.startswith('//'):
                stream_name = f"//{self.depot}/{self.stream}"
                
            if stream_name is not None:
                client_spec["Stream"] = stream_name
            
            # 设置用户传入的 options, 具体选项参考 p4 官方文档
            if options:
                existing_options = client_spec.get("Options", "").split()
                new_options = options.copy()
                
                # 处理互斥选项
                for new_opt in new_options:
                    if new_opt in self._CLIENT_MUTUALLY_EXCLUSIVE:
                        conflict_opt = self._CLIENT_MUTUALLY_EXCLUSIVE[new_opt]
                        if conflict_opt in existing_options:
                            existing_options.remove(conflict_opt)
                
                # 合并并去重（保留原有逻辑）
                all_options = existing_options + new_options
                unique_options = list(set(all_options))
                client_spec["Options"] = " ".join(unique_options)
            
            if line_ending_type:
                if line_ending_type.lower() in self._CLIENT_LINE_ENDING_TYPE:
                    client_spec["LineEnd"] = line_ending_type.lower()
                else:
                    self.logger.error(f"Invalid line end: {line_ending_type}")
                    raise
            self.logger.info(f"client_spec: {client_spec}")
            result = self.p4.save_client(client_spec)
            self.logger.info(f"[create_client result] {result}")
            return True
        except P4Exception as e:
            self.logger.error("create_client failed: %s", str(e))
            return False
    
    def edit_files(self, file_list) -> bool:
        """
        强制将 file_list 中的文件添加至 ChangeList
        Args:
            file_list: 由外部输入 edit 的文件列表
        """

        if not file_list:
            self.logger.info("没有需要编辑的文件")
            return True
        
        try:
            # 单次执行 edit -f，自动从input读取所有文件
            result = self.p4.run_edit('-f', *file_list)
                
            self.logger.info(f"成功编辑 {len(result)} 个文件")
            return True
                
        except P4Exception as e:
            self.logger.error(f"edit_files 失败: {str(e)}")
            return False
            
    
    def delete_client(self, client_name: str = "") -> bool:
        """
        删除P4客户端工作区
        """
        try:
            if not client_name:
                client_name = self.p4.client
            result = self.p4.delete_client("-f", client_name)
            self.logger.info(f"[delete_client result] {result}")
            return True
        except P4Exception as e:
            self.logger.error("delete_client failed: %s", str(e))
            return False
    
    def disconnect(self) -> None:
        """断开与服务器的连接"""
        try:
            if self.p4.connected():
                self.p4.disconnect()
                self.logger.info("Disconnected from server")
        except P4Exception as e:
            self.logger.warning(f"Error disconnecting: {str(e)}")
    
    def __enter__(self):
        """支持上下文管理器"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出时自动断开连接"""
        self.disconnect()
        # 不抑制异常. 确保异常也能正常调用断开连接
        return False  
    
    def sync(self, filespecs: List[str], options: List[str] = []) -> bool:
        """
        拉取缓存到本地
        Args:
            filespecs: sync 文件的路径，例如 //{DepotName}/{StreamName}/...@{Label}
            options: 参数选项, 一般标记是否使用 -f, 强制覆盖本地所有缓存, 这种方式更彻底, 但耗时可能会更长
        """
        try:
            result = self.p4.run_sync(*options, *filespecs)
            self.logger.debug(f"[sync result] {result}")
            return True
        except P4Exception as e:
            self.logger.error(f"Sync failed: {str(e)}")
            return False
    
    def revert(self, filespecs: List[str], options: List[str] = []) -> bool:
        '''
        执行 p4 revert 操作, 将 changelist 变更列表中的 opened 文件回退, 根据原生 p4 命令封装而来
        Args:
            filespecs: revert 文件的路径，例如 //{DepotName}/{StreamName}/...
            options: 参数选项
        '''
        try:
            result = self.p4.run_revert(*options, *filespecs)
            self.logger.debug(f"[revert result] {result}")
            return True
        except P4Exception as e:
            self.logger.error(f"Revert failed: {str(e)}")
            return False
    
    def reconcile(self, filespecs: List[str], options: List[str] = []) -> bool:
        '''
        执行 p4 reconcile 操作, 类似于 git status, 查找当前本地与服务器发生变更的文件
        相比于 git status, reconcile 还会将变更文件添加到 changelist
        Args:
            filespecs: reconcile 文件的路径, 一般会选择对所有文件进行 reconcile, 例如 ["..."]
            options: 可选参数选项, 我们一般添加 -a -d -e -m
        '''
        try:
            result = self.p4.run_reconcile(*options, *filespecs)
            self.logger.debug(f"[reconcile result] {result}")
            return True
        except P4Exception as e:
            self.logger.error(f"Reconcile failed: {str(e)}")
    
    def submit(self, filespecs: List[str], options: List[str] = []) -> bool:
        """
        提交变更到服务器, 在 Bccache 中一般是用来测速任务提交缓存
        Args:
            filespecs: submit 文件的路径, 一般会选择对所有文件进行提交, 例如 //{DEPOT}/{STREAM}...
            options: 可选参数列表, 上传缓存一般使用参数为 -d, 附带提交描述, 描述一般统一采用 submit_label
        """
        try:
            result = self.p4.run_submit(*options, *filespecs)
            self.logger.debug(f"[submit result] {result}")
            return True
        except P4Exception as e:
            self.logger.error(f"Submit failed: {str(e)}")
            return False
    
    def create_label(self, label: str = "") -> bool:
        '''
        创建 label 标签函数, 一般只有测速任务提交新缓存时才会创建 label 标签
        '''
        try:
            if not label:
                label = self.submit_label
            label_spec = self.p4.fetch_label(label)
            
            self.logger.info(f"label_spec: {label_spec}")
            result = self.p4.save_label(label_spec)
            self.logger.info(f"[create_label result] {result}")
            return True
        except P4Exception as e:
            self.logger.error(f"create_label failed: {str(e)}")
            return False
    
    def labelsync(self, filespecs: List[str], options: List[str] = []) -> bool:
        '''
        测速任务的流程一般是 submit 将文件提交到服务器以后, 还需要给当前工作区的状态打标签
        类似于快照, 方便对编译缓存做版本控制, 因此需要借助该函数将工作区的状态同步到服务器指定的标签
        注意: 同步的标签必须在服务器存在, 否则需要调用 create_label 函数先创建标签
        Args:
            filespecs: labelsync 文件的路径, 一般会选择对所有文件进行提交, 例如 //{DEPOT}/{STREAM}...
            options: 可选参数列表, 上传缓存一般使用参数为 -l, 附带标签名, 例如 -l aha_32581_iron_45231
        '''
        try:
            self.p4.run_labelsync(*options, *filespecs)
            return True
        except P4Exception as e:
            self.logger.error(f"Labelsync failed: {str(e)}")
            return False
    
    def add_file(self, filespecs: List[str], options: List[str] = []) -> bool:
        '''
        该函数用于当本地工作区有新增文件, 且未被 P4 服务器管理, 则需要 add 到待提交列表, 随 submit 提交
        Args:
            filespecs: labelsync 文件的路径, 一般会选择对所有文件进行提交, 例如 ...
            options: 可选参数列表
        '''
        try:
            result = self.p4.run_add(*options, *filespecs)
            self.logger.debug(f"[add_file result] {result}")
            return True
        except P4Exception as e:
            self.logger.error(f"add_file failed: {str(e)}")
            return False
        
    def create_depot(self, depot_name:str = "", depot_type: str = "", description: str = "") -> bool:
        '''
        封装创建 depot 函数接口
        Args:
            depot_name: 如果不传入, 默认采用配置文件的 depot_name
            depot_type: depot 的类型, 我们一般需要指定为 stream 类型, 其他类型参考 p4 官方文档
            https://help.perforce.com/helix-core/server-apps/cmdref/current/Content/CmdRef/p4_depot.html#p4_depot:~:text=p4%20protect.-,Form%20Fields,-Field%20Name
        '''
        try:
            if not depot_name:
                depot_name = self.depot
            depots = self.p4.run_depots()
            
            # 由于 P4 对 depot 有严格的限制, 对于已经存在的 depot 是不能更改其信息的
            # 所以在创建 depot 前会进行检查, 对于已存在 depot 不再创建
            for depot in depots:
                if depot["name"].lower() == depot_name.lower():
                    self.logger.warning(f"{depot_name} exists")
                    return False
            depot_spec = self.p4.fetch_depot(depot_name)
            if depot_type:
                depot_spec["Type"] = depot_type.lower()
            if description:
                depot_spec["Description"] = description.lower()
            
            self.logger.info(f"depot_spec: {depot_spec}")
            result = self.p4.save_depot(depot_spec)
            self.logger.info(f'[create_depot result] {result}')
            return True
        except P4Exception as e:
            self.logger.error(f"create_depot failed: {str(e)}")
            return False
        
    def create_stream(self, depot_name: str = "", stream_name: str = "", stream_type: str = "mainline") -> bool:
        '''
        创建 stream 的接口, Bccache 使用 p4 的 depot 是 stream 流式, 所以需要创建 stream
        Agrs:
            depot_name: stream 的创建必须绑定 depot, 因此需要指定 depot_name, 若不指定则默认使用 config 配置的 depot_name
            stream_type: 指定 stream 的类型, 具体类型参考 p4 官方文档, 默认为 mainline
        '''
        try:
            if not depot_name:
                depot_name = self.depot
            if not stream_name:
                stream_name = self.stream
            if depot_name and not depot_name.startswith('//'):
                stream_name = f"//{depot_name}/{stream_name}"
            
            stream_spec = self.p4.fetch_stream(stream_name)
            stream_spec["Type"] = stream_type.lower()
            
            self.logger.info(f"stream_spec: {stream_spec}")
            
            result = self.p4.save_stream(stream_spec)
            self.logger.info(f"[create_stream result] {result}")
            return True
        except P4Exception as e:
            self.logger.error(f"create_stream failed: {str(e)}")
            return False
    
    def delete_stream(self, depot_name: str = "", stream_name: str = "") -> bool:
        '''
        删除 stream 函数接口
        Agrs:
            depot_name: stream 的创建必须绑定 depot, 因此需要指定 depot_name, 若不指定则默认使用 config 配置的 depot_name
        '''
        try:
            if not depot_name:
                depot_name = self.depot
            if not stream_name:
                stream_name = self.stream
            if depot_name and not depot_name.startswith('//'):
                stream_name = f"//{depot_name}/{stream_name}"
            result = self.p4.delete_stream(stream_name)
            self.logger.info(f"[delete_stream result] {result}")
            return True
        except P4Exception as e:
            self.logger.error(f"delete_stream failed: {str(e)}")
            return False
        
    def delete_depot(self, depot_name: str = "") -> bool:
        '''
        删除 depot 函数接口
        '''
        try:
            if not depot_name:
                depot_name = self.depot
            
            result = self.p4.delete_depot(depot_name)
            self.logger.info(f"[delete_depot result] {result}")
            return True
        except P4Exception as e:
            self.logger.error(f"delete_depot failed: {str(e)}")
            return False

    
    def get_label_lists(self, depot_name: str = "", stream_name: str = "") -> Any:
        '''
        获取服务器的 label 列表, 按照更新时间降序排序
        '''
        try:
            if not depot_name:
                depot_name = self.depot
            if not stream_name:
                stream_name = self.stream
            if depot_name and not depot_name.startswith("//"):
                depot_name = f"//{depot_name}"
            
            labels = self.p4.run_changes("-m", "20", "-l", f"{depot_name}/{stream_name}/...")
            # 解析 label 的日期信息并转换为 datetime 对象
            labeled_dates = []
            for label in labels:
                label_name = label['desc']
                label_name = label_name.replace('{', '').replace('}', '')
                
                update_timestamp = int(label['time'])
                # 将 Unix 时间戳转换为 datetime 对象
                update_date = datetime.datetime.fromtimestamp(update_timestamp)
                labeled_dates.append((label_name, update_date))

            
            # 按照日期进行降序排序
            labeled_dates.sort(key=lambda x: x[1], reverse=True)
            
            # 获取最近的 label
            if labeled_dates:
                # 只返回前 20 个 label
                return labeled_dates[:20]
            else:
                self.logger.error(f"在 {depot_name}/{stream_name} 下未找到 label")
                return None
        
        except P4Exception as e:
            self.logger.error(f"get_latest_label failed: {e}")
            
    def check_depot(self, depot_name: str = "") -> bool:
        '''
        检查服务器是否存在用户指定的 depot
        '''
        try:
            if not depot_name:
                depot_name = self.depot
            depots = self.p4.run_depots()
            
            for depot in depots:
                if depot["name"].lower() == depot_name.lower():
                    self.logger.info(f"{depot_name} exists")
                    return True
            
            self.logger.info(f"{depot_name} not exists")
            return False
        except P4Exception as e:
            self.logger.error(f"check_depot failed: {e}")
            return False
        
    def check_stream(self, depot_name: str = "", stream_name: str = "") -> bool:
        '''
        检查服务器是否存在用户指定的 stream
        '''
        try:
            if not depot_name:
                depot_name = self.depot
            if not stream_name:
                stream_name = self.stream
            
            if depot_name and not depot_name.startswith("//"):
                stream_name = f"//{depot_name}/{stream_name}"
            
            streams = self.p4.run_streams()
            
            for stream in streams:
                if stream["name"].lower() == stream_name.lower():
                    self.logger.info(f"{stream_name} exists")
                    return True
            
            self.logger.info(f"{stream_name} not exists")
            return False
        
        except P4Exception as e:
            self.logger.error(f"check_stream failed: {e}")
            return False    
        
    def check_client(self, client_name: str = "") -> bool:
        '''
        检查服务器是否存在用户指定的 client
        '''
        try:
            if not client_name:
                client_name = self.p4.client
                
            clients = self.p4.run_clients()
            
            for client in clients:
                if client["client"].lower() == client_name.lower():
                    self.logger.info(f"{client_name} exists")
                    return True
                
            self.logger.info(f"{client_name} not exists")
            return False
        except P4Exception as e:
            self.logger.error(f"check_client failed: {e}")
            return False

    def get_opened_files(self, options: List[str]) -> List:
        '''
        获取处于 opened 状态的 files 列表, 即被加入到 changelist 的文件
        
        Args:
            options: 选项参数, 必填选项为 -c, 指定 changelist 变更列表, 例如 ["-c", "default"]
        '''
        try:
            opened_files = self.p4.run_opened(*options)
            self.logger.debug(f"opened_files: {opened_files}")
            return opened_files
        except P4Exception as e:
            self.logger.error(f"get_opened_files failed: {e}")
            return []
    
    @property
    def port(self):
        return self.p4.port
    
    @property
    def user(self):
        return self.p4.user
    
    @property
    def client(self):
        return self.p4.client
    
    @property
    def password(self):
        return self.p4.password
    
    @property
    def depot(self):
        return self._depot
    
    @property
    def stream(self):
        return self._stream
    
    @property
    def sync_label(self):
        return self._sync_label
    
    @property
    def submit_label(self):
        return self._submit_label
    
    @property
    def work_dir(self):
        return self._work_dir
    
if __name__ == "__main__":
    pass