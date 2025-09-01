from base.log import log_util
from base.ninja import ninja_util
from base.tos import tos_util

class PostCompile:
    '''
    PostCompile 位于编译后阶段, 对外提供以下接口:
    1. 生成 .diff_ninja_log 并保存至远端: 
        无论是 CI 检查任务还是测速任务, 编译完成以后都需要生成 .diff_ninja_log
        相当于是记录本次的编译 obj 文件状态, 为下一次编译做准备
    2. 从远端获取 .diff_ninja_log 文件
        对于 CI 检查任务, 需要获取上一次编译产生的 .diff_ninja_log 文件, 对其中的
        target 进行 revert, 不让其影响本次编译
        对于测速任务, 需要获取上一次编译产生的 .diff_ninja_log 文件, 将其中的 target
        进行 submit, 防止上传缓存不全
    '''
    
    _logger = log_util.BccacheLogger(name="PostCompile")
    
    @classmethod
    def create_diff_ninja_log(cls, ninja_log_path: str, build_dir: str, ninja_exe_path: str, diff_ninja_log_file_key: str) -> bool:
        '''
        对外提供的接口, 在编译完以后调用, 完成 .diff_ninja_log 的构建以及上传
        
        Args:
            ninja_log_path: .ninja_log 在编译机本地的路径
            build_dir: 编译机上的 out 编译目录
            ninja_exe_path: ninja 可执行程序的路径
            diff_ninja_log_file_key: 在 tos 上 .diff_ninja_log 的路径
        '''
        ninja = ninja_util.NinjaUtil(build_dir=build_dir, executable=ninja_exe_path)
        # 生成 .diff_ninja_log 文件
        diff_ninja_log_path = ninja.get_diff_ninja_log(ninja_log_path=ninja_log_path)
        if diff_ninja_log_path is None:
            cls._logger.error(f"get_diff_ninja_log error")
            return False
        # 上传 .diff_ninja_log 文件
        if not tos_util.BlazeCacheTos.upload_file(local_file_path=diff_ninja_log_path, remote_file_path=diff_ninja_log_file_key):
            cls._logger.error(f"upload .diff_ninja_log error")
            return False
        return True
    
    @classmethod
    def get_diff_ninja_log(cls, local_diff_ninja_log_path: str, diff_ninja_log_file_key: str) -> bool:
        '''
        对外提供的接口, 在编译前调用, 从 tos 远端下载 .diff_ninja_log 到本地
        '''
        
        if not tos_util.BlazeCacheTos.download_file(local_file_path=local_diff_ninja_log_path, remote_file_path=diff_ninja_log_file_key):
            return False
        return True
        