import os
import shutil
import sys
import time
import urllib.request
from base.log import log_util


def Retry(func, times, *args, **kwargs):
    '''
    重试函数, 文件操作容易因资源竞争导致失败, 因此需要失败后重试
    '''
    for _ in range(times):
        value = func(*args, **kwargs)  
        if value:
            return value
        time.sleep(5)
    return False

class FileUtil:
    '''
    封装常用的文件操作工具, 方便快速完成文件操作
    '''
    logger = log_util.BccacheLogger(name="FileUtil")
    
    @classmethod
    def remove_folder(cls, folder: str, retry_times: int = 5) -> bool:
        def remove_folder_impl():
            if not os.path.exists(folder):
                cls.logger.info('[RemoveFolder]', folder, 'not existed')
                return True

            cls.logger.info('[RemoveFolder]', 'Delete', folder)
            try:
                shutil.rmtree(folder)
            except BaseException as e:
                cls.logger.error('[RemoveFolder]', e)

            ret = not os.path.exists(folder)
            cls.logger.info('[RemoveFolder]', 'Delete', folder,
                'success' if ret else 'failure')
            return ret

        Retry(remove_folder_impl, retry_times)
        
    @classmethod
    def remove_file(cls, file: str, retry_times: int = 5) -> bool:
        def remove_file_impl():
            try:
                if not os.path.exists(file):
                    cls.logger.info('[RemoveFile]', file, 'not existed')
                    return True

                cls.logger.info('[RemoveFile]', 'Delete', file)
                os.remove(file)
            except BaseException as e:
                cls.logger.error('[RemoveFile]', e)

            ret = not os.path.exists(file)
            cls.logger.info('[RemoveFile]', 'Delete', file, 'success' if ret else 'failure')
            return ret

        Retry(remove_file_impl, retry_times)
    
    @classmethod
    def get_folder_size(cls, folder: str, details: dict = {}) -> int:
        '''
        计算指定目录的 size 大小, 一般会用来统计 out 缓存目录的大小, 做调试确认信息使用
        
        Agrs:
            folder: 目录路径名
            details: 可选参数, 用于收集目录中每个文件和子目录的详细大小信息
            
        Returns:
            返回整个目录的总体积
        '''
        if folder is None:
            return 0

        if not os.path.exists(folder):
            return 0

        size = 0
        for r in os.listdir(folder):
            item = os.path.join(folder, r)

            if os.path.islink(item) or os.path.isfile(item):
                item_size = os.path.getsize(item)
                # 链接符号不计算大小, 主要是两层考虑
                # 1. 链接文件指向的实体若不在 folder 下, 则不应该计算大小
                # 2. 链接文件指向的实体若在 folder 下, 则会重复计算大小
                # 但需要将 folder 的所有文件记录添加至 details 中
                if os.path.islink(item):
                    item_size = 0
                if details is not None:
                    details[r] = item_size
                size += item_size

            elif os.path.isdir(item):
                temp_tails = {}
                size += cls.FolderSize(item, temp_tails)
                if details is not None:
                    details[r] = temp_tails

        return size
    
    @classmethod
    def make_directory_exists(cls, dirname: str) -> bool:
        if dirname is None or dirname == '':
            return False

        cls.logger.info(f"[make] Make {dirname} existed")
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return True
    
    @classmethod
    def download_url(cls, url: str, local_path: str) -> bool:
        cls.logger.info(f"download {url} => {local_path}")
        def DownloadURL_Impl():
            try:
                if os.path.dirname(local_path) != '':
                    if not os.path.exists(os.path.dirname(local_path)):
                        cls.make_directory_exists(os.path.dirname(local_path))
                urllib.request.urlretrieve(url, local_path)
                return True
            except BaseException as e:
                cls.logger.error(f"[download] error: {e}")
                return False
        if not Retry(DownloadURL_Impl, 50):
            cls.logger.error(f"Fail to download {url}")
            return False
    
class ChangeDirectory:

    def __init__(self, new_directory):
        self.new_directory = new_directory
        self.current_directory = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_directory)

    def __exit__(self, exc_type, exc_value, trace):
        os.chdir(self.current_directory)
