import logging
import time
import multiprocessing
from pathlib import Path
from typing import List, Union
import sys
import os
from base.log.log_util import BccacheLogger 
class TimeStampUtil:
    def __init__(self, target_time: Union[int, float, str], 
                 exclude_dirs: List[str] = None, 
                 exclude_extensions: List[str] = None,
                 max_workers: int = None):
        """
        初始化时间戳修改器
        
        参数:
            target_time: 目标时间，可以是时间戳(int/float)或字符串(YYYY-MM-DD HH:MM:SS)
            exclude_dirs: 要排除的目录名称列表
            exclude_extensions: 要排除的文件扩展名列表
            max_workers: 最大工作进程数，默认使用CPU核心数
        """
        self.target_time = self._parse_time(target_time)
        self.exclude_dirs = set(exclude_dirs or ['.git', 'out', '.cargo', '.codebase'])
        self.exclude_extensions = set(exclude_extensions or [])
        self.max_workers = max_workers or multiprocessing.cpu_count()
        
        # 初始化日志记录器
        self.logger = BccacheLogger(name="TimeStampUtil", level=logging.INFO)

    def _parse_time(self, time_value: Union[int, float, str]) -> float:
        """解析时间值为时间戳"""
        if isinstance(time_value, (int, float)):
            return float(time_value)
        elif isinstance(time_value, str):
            try:
                struct_time = time.strptime(time_value, '%Y-%m-%d %H:%M:%S')
                return time.mktime(struct_time)
            except ValueError:
                raise ValueError("时间格式不正确，使用YYYY-MM-DD HH:MM:SS格式")
        else:
            raise TypeError("不支持的时间类型")
    
    def _should_exclude(self, path: Path) -> bool:
        """检查路径是否应该被排除"""
        for part in path.parts:
            if part in self.exclude_dirs:
                return True
        if any(path.suffix == ext for ext in self.exclude_extensions):
            return True
        return False
    
    def _modify_timestamp(self, file_path: Path) -> tuple:
        """修改单个文件的时间戳"""
        try:
            os.utime(file_path, (self.target_time, self.target_time))
            return 1, 0  # 成功计数
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return 0, 1  # 错误计数
    
    def _scan_directory_worker(self, root_dir: Path) -> tuple:
        """工作进程函数：扫描目录并返回文件列表"""
        skipped = 0
        files = []
        
        try:
            for entry in os.scandir(root_dir):
                entry_path = Path(entry.path)
                if entry.is_dir(follow_symlinks=False):
                    if self._should_exclude(entry_path):
                        # 跳过整个排除目录
                        skipped_sub = sum(1 for _ in entry_path.rglob('*')) if entry.is_dir() else 0
                        skipped += skipped_sub
                    else:
                        # 递归扫描子目录
                        sub_skipped, sub_files = self._scan_directory_worker(entry_path)
                        skipped += sub_skipped
                        files.extend(sub_files)
                elif entry.is_file(follow_symlinks=False):
                    if not self._should_exclude(entry_path):
                        files.append(entry_path)
            
            return skipped, files
            
        except Exception as e:
            self.logger.error(f"Error scanning {root_dir}: {e}")
            return 0, []  # 返回空结果，避免异常传播
    
    def process_directory(self, root_dir: str) -> dict:
        """
        处理目录及其子目录中的所有文件
        
        参数:
            root_dir: 根目录路径
        
        返回:
            处理统计信息
        """
        root_path = Path(root_dir).resolve()
        if not root_path.is_dir():
            self.logger.error(f"{root_dir} 不是一个目录")
            raise NotADirectoryError(f"{root_dir} 不是一个目录")
        
        self.logger.info("正在并行扫描目录...")
        scan_start = time.time()
        
        # 收集需要扫描的顶级目录
        top_level_dirs = []
        root_files = []
        root_skipped = 0
        
        try:
            for entry in os.scandir(root_path):
                entry_path = Path(entry.path)
                if entry.is_dir(follow_symlinks=False):
                    if self._should_exclude(entry_path):
                        # 跳过整个排除目录
                        skipped_sub = sum(1 for _ in entry_path.rglob('*'))
                        root_skipped += skipped_sub
                    else:
                        top_level_dirs.append(entry_path)
                elif entry.is_file(follow_symlinks=False):
                    if not self._should_exclude(entry_path):
                        root_files.append(entry_path)
        except Exception as e:
            self.logger.error(f"Error scanning root directory: {e}")
        
        # 使用进程池并行扫描顶级目录
        with multiprocessing.Pool(processes=min(self.max_workers, len(top_level_dirs) or 1)) as pool:
            results = pool.map(self._scan_directory_worker, top_level_dirs)
        
        # 汇总扫描结果
        total_files = root_files
        total_skipped = root_skipped
        
        for skipped, files in results:
            total_skipped += skipped
            total_files.extend(files)
        
        scan_end = time.time()
        
        self.logger.info(f"扫描完成: {len(total_files)} 个文件需要处理，{total_skipped} 个文件被跳过")
        self.logger.info(f"扫描耗时: {scan_end - scan_start:.2f} 秒")
        
        # 使用进程池处理文件
        self.logger.info(f"开始处理，使用 {self.max_workers} 个工作进程...")
        process_start = time.time()
        
        with multiprocessing.Pool(processes=self.max_workers) as pool:
            results = pool.map(self._modify_timestamp, total_files)
        
        process_end = time.time()
        
        # 汇总结果
        processed, errors = zip(*results)
        total_processed = sum(processed)
        total_errors = sum(errors)
        
        stats = {
            'processed': total_processed,
            'skipped': total_skipped,
            'errors': total_errors,
            'scan_time': scan_end - scan_start,
            'process_time': process_end - process_start,
            'total_time': (process_end - process_start) + (scan_end - scan_start),
            'throughput': total_processed / (process_end - process_start) if (process_end - process_start) > 0 else 0
        }
        
        return stats


