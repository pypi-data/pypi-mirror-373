import bytedtos
import os
from base.log import log_util
from base.file import file_util


class BlazeCacheTos:
    """
    封装 blazecache 的 tos 存储服务
    """

    _ACCESS_KEY = "7O7GF5YBG92NR3SZUJQB"
    _BUCKET_NAME = "blazecache-cn"
    _SECRET_KEY = "5wF35DlBhz3zjRlzp1eEz+8KN984Mv4XGBd91ofl"

    # 根据 Tos 官方文档, 使用 endpoint 方式接入不需要配置 Consul 环境, 接入更方便
    # 缺点在于限速 5mb/s，但实际上全量 .ninja_log 的大小在 15mb 左右, 影响能接受
    _ENDPOINT = "tos-cn-north.byted.org"
    # 请求超时时间, 默认设置为 60s
    _REQUEST_TIMEOUT = 60
    # 连接超时时间，默认设置为 60s
    _CONNECT_TIMEOUT = 60
    # 连接池大小
    _CONNECT_POOL_SIZE = 10
    
    _logger = log_util.BccacheLogger(name="BlazeCacheTos")

    @classmethod
    def _create_client(cls):
        return bytedtos.Client(
            cls._BUCKET_NAME,
            cls._ACCESS_KEY,
            endpoint=cls._ENDPOINT,
            timeout=cls._REQUEST_TIMEOUT,
            connect_timeout=cls._CONNECT_TIMEOUT,
            connection_pool_size=cls._CONNECT_POOL_SIZE,
        )
    
    @classmethod
    def upload_file(cls, local_file_path: str, remote_file_path: str, retry_times: int = 5) -> bool:
        '''
        上传文件到 blazecache 的 tos 中, 有两种上传方式, 普通上传与分片上传
        会根据文件大小, 设置临界值为 100mb, 超过 100mb 采用分片上传
        blazecache 的 tos put 限速 10mb/s, QPS=10
        假设 100mb 分成 10 片, 可以并行上传, 提高大文件传输的效率
        
        Args:
            local_file_path: 需要上传的文件绝对路径(本地)
            remote_file_path: 上传到 tos 的目标路径
            retry_times: 上传失败的重试次数, 默认重试 5 次
        '''
        local_file_path = local_file_path.strip()
        remote_file_path = remote_file_path.strip()
        if local_file_path is None or remote_file_path is None:
            cls._logger.warning(f"{local_file_path} or {remote_file_path} is None")
            return False
        client = cls._create_client()
        file_total_size = os.path.getsize(local_file_path)
        cls._logger.info(f"{local_file_path} size: {file_total_size}")
        # 设置临界大小为 100mb，如果上传文件大于 100mb，将采用分片上传
        key_size = 100 *1024 * 1024

        def upload_impl():
            try:
                with open(local_file_path, 'rb') as f:
                    file_size = os.path.getsize(local_file_path)
                    base_name = os.path.basename(local_file_path)
                    cls._logger.info(f"begin upload {local_file_path} to {remote_file_path}")
                    content = f.read()
                    resp = client.put_object(remote_file_path, content)
                    cls._logger.info(f"upload: {local_file_path}, resp code: {resp.status_code}")
                    return True
            except bytedtos.TosException as e:
                cls._logger.error(f"failed to upload: {local_file_path}, code: {e.code}, request_id: {e.request_id}, message: {e.msg}")
                return False
        def parted_upload_impl():
            try:
                init_response = client.init_upload(remote_file_path)
                upload_id = init_response.upload_id
                parts_list = []
                # 设置每次分片上传大小为 10mb
                part_size = 10 * 1024 * 1024
                with open(local_file_path, 'rb') as f:
                    part_number = 1
                    offset = 0
                    while offset < file_total_size:
                        if file_total_size - offset < 2*part_size:
                            num_to_upload = file_total_size - offset
                        else:
                            num_to_upload = min(part_size, file_total_size - offset)
                        f.seek(offset, os.SEEK_SET)
                        cur_data = f.read(num_to_upload)
                        upload_part_resp = client.upload_part(remote_file_path, upload_id, part_number, cur_data)
                        parts_list.append(upload_part_resp.part_number)
                        offset += num_to_upload
                        part_number += 1
                comp_resp = client.complete_upload(remote_file_path, upload_id, parts_list)
                cls._logger.info(f"partedUpload success. code: {comp_resp.status_code}")  
                return True
            except bytedtos.TosException as e:
                cls._logger.error(f"partedUpload failed. code: {e.code}, request_id: {e.request_id}, message: {e.msg}")
                return False

        
        if file_total_size > key_size:
            return file_util.Retry(parted_upload_impl, retry_times)
        else:
            return file_util.Retry(upload_impl, retry_times)
        
    
    @classmethod
    def download_file(cls, local_file_path: str, remote_file_path: str, retry_times: int = 5) -> bool:
        '''
        从 blazecache 的 tos 中下载文件对象并保存在指定的本地文件中
        
        Args:
            local_file_path: 本地保存文件路径
            remote_file_path: 远端下载文件路径
            retry_times: 重试次数, 默认为 5 次
        '''
        local_file_path = local_file_path.strip()
        remote_file_path = remote_file_path.strip()

        if not cls.check_remote_file_exist(remote_file_path):
            cls._logger.error(f"file not existed {remote_file_path}")
            return False

        def download_impl():
            with open(local_file_path, 'wb') as f:
                try:
                    client = cls._create_client()
                    resp = client.get_object(remote_file_path)
                    cls._logger.info(f"download {remote_file_path} success. code: {resp.status_code}")
                    f.write(resp.data)
                    return True
                except bytedtos.TosException as e:
                    cls._logger.error(f"failed to download {remote_file_path}. code: {e.code}, request_id: {e.request_id}, message: {e.msg}")
                    return False
                
        return file_util.Retry(download_impl, retry_times)
    
    @classmethod
    def upload_object(cls, content, remote_file_path: str, retry_times: int = 5) -> bool:
        '''
        区别于上传文件, 该接口上传单一的对象, content 可以是 str 类型或者 bytes 类型
        '''
        remote_file_path = remote_file_path.strip()
        
        def upload_impl():
            try:
                client = cls._create_client()
                resp = client.put_object(remote_file_path, content)
                cls._logger.info(f"upload: {content}, resp code: {resp.status_code}")
                return True
            except bytedtos.TosException as e:
                cls._logger.error(f"failed to upload: {content}, code: {e.code}, request_id: {e.request_id}, message: {e.msg}")
                return False
            
        return file_util.Retry(upload_impl, retry_times)
    
    @classmethod
    def get_object(cls, remote_file_path: str, retry_times: int = 5):
        '''
        区别于下载文件, 该接口用于获取单一对象
        '''
        remote_file_path = remote_file_path.strip()
        
        def download_impl():
            try:
                client = cls._create_client()
                resp = client.get_object(remote_file_path)
                return resp.data
            except bytedtos.TosException as e:
                    cls._logger.error(f"failed to download {remote_file_path}. code: {e.code}, request_id: {e.request_id}, message: {e.msg}")
                    return False
                
        
        return file_util.Retry(download_impl, retry_times)
        
                
    
    @classmethod
    def check_remote_file_exist(cls, remote_file_path: str) -> bool:
        '''
        检查 tos 远端是否存在指定的文件
        '''
        if remote_file_path.startswith('http'):
            remote_file_path = cls.file_key_from_url(remote_file_path)
        try:
            client = cls._create_client()
            ret = client.head_object(remote_file_path)
            return ret is not None
        except BaseException as e:
            cls._logger.warning(f"fail to check_remote_file_exist {remote_file_path}")
            return False
        
    @classmethod
    def file_key_from_url(cls, url: str):
        if url is None:
            return None
        index = url.find(cls._BUCKET_NAME)
        if index >= 0:
            return url[index + len(cls._BUCKET_NAME) + 1:]
        else:
            return url
        
    @classmethod
    def get_diff_ninja_log_file_key(cls, product_name: str, os_type: str, job_type: str, branch_type: str, machine_id: str, id: str) -> str:
        '''
        规范化 .diff_ninja_log 存储在 tos 中的路径区分
        '''
        diff_ninja_log_path = f"diff_ninja_log/{product_name.lower()}/{os_type.lower()}/{job_type.lower()}/{branch_type.lower()}/{machine_id.lower()}/{id.lower()}/.diff_ninja_log"
        return diff_ninja_log_path
    
    @classmethod
    def get_diff_ninja_log_id_file_key(cls, product_name: str, os_type: str, job_type: str, branch_type: str, machine_id: str) -> str:
        '''
        tos 还会存储 diff_ninja_log_id 信息, 通过访问固定的 file_key
        就能获取基于 product_name/os_type/job_type/branch_type/machine_id 的上一个 .diff_ninja_log 的 id
        .diff_ninja_log 的 id 是自增的
        注意, 该函数只返回规范化的 file_key, 需要获取到 file_key 后通过
        '''
        file_key = f"diff_ninja_log_id/{product_name.lower()}/{os_type.lower()}/{job_type.lower()}/{branch_type.lower()}/{machine_id.lower()}"
        return file_key
        

if __name__ == "__main__":
    # BlazeCacheTos.upload_file(local_file_path="/Users/bytedance/Desktop/lark/src/out/release_apollo_arm64/.diff_ninja_log",
    #                           remote_file_path="test/.diff_ninja_log")
    
    # BlazeCacheTos.upload_file(local_file_path="/Users/bytedance/Desktop/lark/src/out/release_apollo_arm64/.ninja_log",
    #                           remote_file_path="test/.ninja_log")

    # BlazeCacheTos.download_file(local_file_path="./.ninja_log", remote_file_path="test/.ninja_log")
    content = "100"
    remote_file_path = BlazeCacheTos.get_diff_ninja_log_id_file_key(product_name="lark", os_type="dawin", job_type="ci_check_task", branch_type="main", machine_id="1234")
    BlazeCacheTos.upload_object(content=content, remote_file_path=remote_file_path)
    data = BlazeCacheTos.get_object(remote_file_path=remote_file_path)
    print(data.decode("utf-8"))