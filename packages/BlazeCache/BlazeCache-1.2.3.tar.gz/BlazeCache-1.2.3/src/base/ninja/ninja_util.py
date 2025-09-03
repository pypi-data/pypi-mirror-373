import fnmatch
import os
import subprocess
from base.log import log_util
from datetime import datetime
from base.file import file_util
from pathlib import Path
from typing import List, Optional, Dict

# [Chromium]
# The number of long build times to report:
long_count = 10
# The number of long times by extension to report
long_ext_count = 10

# [Chromium]
class Target:
    """Represents a single line read for a .ninja_log file."""
    def __init__(self, start, end):
        """Creates a target object by passing in the start/end times in seconds
        as a float."""
        self.start = start
        self.end = end
        # A list of targets, appended to by the owner of this object.
        self.targets = []
        self.weighted_duration = 0.0

    def Duration(self):
        """Returns the task duration in seconds as a float."""
        return self.end - self.start

    def SetWeightedDuration(self, weighted_duration):
        """Sets the duration, in seconds, passed in as a float."""
        self.weighted_duration = weighted_duration

    def WeightedDuration(self):
        """Returns the task's weighted duration in seconds as a float.

        Weighted_duration takes the elapsed time of the task and divides it
        by how many other tasks were running at the same time. Thus, it
        represents the approximate impact of this task on the total build time,
        with serialized or serializing steps typically ending up with much
        longer weighted durations.
        weighted_duration should always be the same or shorter than duration.
        """
        # Allow for modest floating-point errors
        epsilon = 0.000002
        if self.weighted_duration > self.Duration() + epsilon:
            print("%s > %s?" % (self.weighted_duration, self.Duration()))
        assert self.weighted_duration <= self.Duration() + epsilon
        return self.weighted_duration

    def DescribeTargets(self):
        """Returns a printable string that summarizes the targets."""
        # Some build steps generate dozens of outputs - handle them sanely.
        # The max_length was chosen so that it can fit most of the long
        # single-target names, while minimizing word wrapping.
        result = ", ".join(self.targets)
        max_length = 65
        if len(result) > max_length:
            result = result[:max_length] + "..."
        return result

# [Chromium]
def GetExtension(target, extra_patterns):
  """Return the file extension that best represents a target.

  For targets that generate multiple outputs it is important to return a
  consistent 'canonical' extension. Ultimately the goal is to group build steps
  by type."""
  for output in target.targets:
    if extra_patterns:
      for fn_pattern in extra_patterns.split(';'):
        if fnmatch.fnmatch(output, '*' + fn_pattern + '*'):
          return fn_pattern
    # Not a true extension, but a good grouping.
    if output.endswith('type_mappings'):
      extension = 'type_mappings'
      break

    # Capture two extensions if present. For example: file.javac.jar should be
    # distinguished from file.interface.jar.
    root, ext1 = os.path.splitext(output)
    _, ext2 = os.path.splitext(root)
    extension = ext2 + ext1 # Preserve the order in the file name.

    if len(extension) == 0:
      extension = '(no extension found)'

    if ext1 in ['.pdb', '.dll', '.exe']:
      extension = 'PEFile (linking)'
      # Make sure that .dll and .exe are grouped together and that the
      # .dll.lib files don't cause these to be listed as libraries
      break
    if ext1 in ['.so', '.TOC']:
      extension = '.so (linking)'
      # Attempt to identify linking, avoid identifying as '.TOC'
      break
    # Make sure .obj files don't get categorized as mojo files
    if ext1 in ['.obj', '.o']:
      break
    # Jars are the canonical output of java targets.
    if ext1 == '.jar':
      break
    # Normalize all mojo related outputs to 'mojo'.
    if output.count('.mojom') > 0:
      extension = 'mojo'
      break
  return extension

# [Chromium]
def SummarizeEntries(entries, extra_step_types):
    global build_file_entries, build_file_entries_time
    """Print a summary of the passed in list of Target objects."""

    # Create a list that is in order by time stamp and has entries for the
    # beginning and ending of each build step (one time stamp may have multiple
    # entries due to multiple steps starting/stopping at exactly the same time).
    # Iterate through this list, keeping track of which tasks are running at all
    # times. At each time step calculate a running total for weighted time so
    # that when each task ends its own weighted time can easily be calculated.
    task_start_stop_times = []
    earliest = -1
    latest = 0
    total_cpu_time = 0
    for target in entries:
      if earliest < 0 or target.start < earliest:
        earliest = target.start
      if target.end > latest:
        latest = target.end
      total_cpu_time += target.Duration()
      task_start_stop_times.append((target.start, 'start', target))
      task_start_stop_times.append((target.end, 'stop', target))
    length = latest - earliest
    weighted_total = 0.0

    # Sort by the time/type records and ignore |target|
    task_start_stop_times.sort(key=lambda times: times[:2])
    # Now we have all task start/stop times sorted by when they happen. If a
    # task starts and stops on the same time stamp then the start will come
    # first because of the alphabet, which is important for making this work
    # correctly.
    # Track the tasks which are currently running.
    running_tasks = {}
    # Record the time we have processed up to so we know how to calculate time
    # deltas.
    last_time = task_start_stop_times[0][0]
    # Track the accumulated weighted time so that it can efficiently be added
    # to individual tasks.
    last_weighted_time = 0.0
    # Scan all start/stop events.
    for event in task_start_stop_times:
      time, action_name, target = event
      # Accumulate weighted time up to now.
      num_running = len(running_tasks)
      if num_running > 0:
        # Update the total weighted time up to this moment.
        last_weighted_time += (time - last_time) / float(num_running)
      if action_name == 'start':
        # Record the total weighted task time when this task starts.
        running_tasks[target] = last_weighted_time
      if action_name == 'stop' and target in running_tasks:
        # Record the change in the total weighted task time while this task ran.
        weighted_duration = last_weighted_time - running_tasks[target]
        target.SetWeightedDuration(weighted_duration)
        weighted_total += weighted_duration
        del running_tasks[target]
      last_time = time
    # assert(len(running_tasks) == 0)

    # Warn if the sum of weighted times is off by more than half a second.
    if abs(length - weighted_total) > 500:
      print('Warning: Possible corrupt ninja log, results may be '
            'untrustworthy. Length = %.3f, weighted total = %.3f' % (
            length, weighted_total))

    # Print the slowest build steps (by weighted time).
    print('    Longest build steps:')
    entries.sort(key=lambda x: x.WeightedDuration())
    for target in entries[-long_count:]:
      print('      %8.1f weighted s to build %s (%.1f s elapsed time)' % (
            target.WeightedDuration(),
            target.DescribeTargets(), target.Duration()))

    # Sum up the time by file extension/type of the output file
    count_by_ext = {}
    time_by_ext = {}
    weighted_time_by_ext = {}
    # Scan through all of the targets to build up per-extension statistics.
    for target in entries:
      extension = GetExtension(target, extra_step_types)
      time_by_ext[extension] = time_by_ext.get(extension, 0) + target.Duration()
      weighted_time_by_ext[extension] = weighted_time_by_ext.get(extension,
              0) + target.WeightedDuration()
      count_by_ext[extension] = count_by_ext.get(extension, 0) + 1

    print('    Time by build-step type:')
    # Copy to a list with extension name and total time swapped, to (time, ext)
    weighted_time_by_ext_sorted = sorted((y, x) for (x, y) in
                                          weighted_time_by_ext.items())
    # Print the slowest build target types (by weighted time):
    for time, extension in weighted_time_by_ext_sorted[-long_ext_count:]:
        print('      %8.1f s weighted time to generate %d %s files '
               '(%1.1f s elapsed time sum)' % (time, count_by_ext[extension],
                                        extension, time_by_ext[extension]))

    print('    %.1f s weighted time (%.1f s elapsed time sum, %1.2fx '
          'parallelism) weighted_total:%.2f s' % (length, total_cpu_time,
          total_cpu_time * 1.0 / length, weighted_total))
    print('    %d build steps completed, average of %1.2f/s' % (
          len(entries), len(entries) / (length)))
    build_file_entries = len(entries)
    build_file_entries_time = length

def ReadTargets(log):
    """Reads all targets from .ninja_log file |log|, sorted by duration.

    The result is a list of Target objects and the content of the diff log."""
    header = log.readline()
    if not header:
        return [], '# ninja log v6\n'
    
    assert header in ("# ninja log v5\n", "# ninja log v6\n"), (
        "unrecognized ninja log version %r" % header)
    
    # 读取所有行并找到最后一个BlazeCache标记
    lines = log.readlines()
    blaze_index = -1
    
    # 从后向前查找BlazeCache标记
    for i in range(len(lines) - 1, -1, -1):
        if "[BlazeCache Flag]" in lines[i]:
            blaze_index = i
            break
    
    # 如果没找到标记，抛出异常
    if blaze_index == -1:
        raise ValueError("在ninja_log文件中未找到[BlazeCache Flag]标记")
    
    # 提取当前构建的日志行（从标记后一行到文件末尾）
    current_build_lines = lines[blaze_index + 1:]
    
    # 解析构建步骤
    targets_dict = {}
    diff_log_lines = []
    
    for line in current_build_lines:
        parts = line.strip().split('\t')
        if len(parts) != 5:
            continue  # 跳过格式错误的行
        
        start, end, _, name, cmdhash = parts
        start = int(start) / 1000.0
        end = int(end) / 1000.0
        
        target = None
        if cmdhash in targets_dict:
            target = targets_dict[cmdhash]
        
        if not target:
            targets_dict[cmdhash] = target = Target(start, end)
        
        target.targets.append(name)
        diff_log_lines.append(line)
    
    # 生成diff_log内容（包含头部）
    diff_log_content = '# ninja log v6\n' + ''.join(diff_log_lines)
    
    return list(targets_dict.values()), diff_log_content

class NinjaUtil:
    """
    Ninja 构建系统工具类, 核心功能: 
    1. 封装常用的 ninja 命令, 用于构建与分析
    2. 提供生成 .diff_ninja_log 的功能, 获取单次构建编译产物列表
    3. 提供单次生成耗时类信息输出能力
    """
    
    def __init__(self, build_dir: str, executable: str):
        """
        初始化 Ninja 工具类
        
        Args:
            build_dir: 执行 Ninja 的构建目录, 用户必须传入, 无默认值
            executable: Ninja 可执行文件路径, 用户必须传入, 一般为 depot_tools 目录下
        """
        self._build_dir = Path(build_dir).resolve()
        self._executable = executable
        self._logger = log_util.BccacheLogger(name="NinjaUtil")
        
        # 确保构建目录存在
        if not self._build_dir.exists():
            file_util.FileUtil.make_directory_exists(self._build_dir)
    
    def run_ninja(self, args: List[str], env: Optional[Dict[str, str]] = None) -> int:
        """
        一个高度自由的运行 Ninja 命令接口, 根据用户传递的参数以及环境变量, 执行对应的 Ninja 指令
        不局限于 Ninja 编译命令
        Args:
            args: 命令行参数列表
            env: 环境变量字典
            
        Returns:
            返回码: 0 表示成功，非零表示失败
        """
        cmd = [self._executable] + args
        self._logger.info(f"执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self._build_dir,
                env={**os.environ, **(env or {})},
                capture_output=True,
                text=True,
                check=False
            )
            
            # 记录标准输出和错误输出
            if result.stdout:
                self._logger.info(f"标准输出:\n{result.stdout}")
            if result.stderr:
                self._logger.error(f"错误输出:\n{result.stderr}")
            
            return result.returncode
            
        except Exception as e:
            self._logger.error(f"执行 Ninja 命令时发生异常: {e}")
            return 1
    
    def list_targets(self) -> List[str]:
        """
        列出所有可用的构建目标
        
        Returns:
            构建目标列表
        """
        try:
            result = subprocess.run(
                [self._executable, "-t", "targets", "all"],
                cwd=self._build_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return [line.split(":")[0].strip() for line in result.stdout.splitlines() if line.strip()]
        except Exception as e:
            self._logger.error(f"获取目标列表失败: {e}")
            return []
    
    def get_version(self) -> Optional[str]:
        """
        获取 Ninja 版本
        
        Returns:
            Ninja 版本字符串，失败时返回 None
        """
        try:
            result = subprocess.run(
                [self._executable, "--version"],
                cwd=self._build_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return None
        
    def insert_flag_to_ninja_log(self, ninja_log_path: str = "") -> bool:
        '''
        向 .ninja_log 中插入一条标记, 该函数必须在编译之前被调用, 记录编译的起始位置
        将来生成 .diff_ninja_log 时需要依据该标记位
        
        Agrs:
            ninja_log_path: 指定生成 .ninja_log 的文件路径, 默认在 ninja 编译产物生成目录下
        '''
        try:
            if not ninja_log_path:
                ninja_log_path = os.path.join(self._build_dir, ".ninja_log")
            
            # 检查文件是否存在，如果不存在则创建
            if not Path(ninja_log_path).exists():
                # 创建文件并写入标准的 ninja log 头部
                with open(ninja_log_path, 'w') as f:
                    f.write('# ninja log v6\n')
                    
            # 向文件末尾追加标记
            with open(ninja_log_path, 'a') as f:
                f.write(f'# [BlazeCache Flag] Build started at {datetime.now().isoformat()}\n')
                
            self._logger.info(f"成功插入编译标记到 {ninja_log_path}")
            return True
        
        except Exception as e:
            self._logger.error(f"插入编译标记失败: {e}")
            return False
        
    def get_diff_ninja_log(self, ninja_log_path: str = ""):
        '''
        根据 .ninja_log 生成 .diff_ninja_log, 逻辑参考了 Chromium 官方的 post_build_ninja_summary.py 脚本
        但因其存在 .ninja_log 并非完全按照 target end 结束时间递增排序的问题
        所以对生成 .diff_ninja_log 的逻辑进行了修改: 从后往前读取 BlazeCache 标记位, 每个标记位代表一次新的构建
        '''
        try:
            # 如果没有指定 .ninja_log 的文件路径, 默认到 ninja 构建产物目录中获取
            if not ninja_log_path:
                ninja_log_path = os.path.join(self._build_dir, ".ninja_log")
                        
            # 检查 .ninja_log 是否存在, 不存在无法构建 .diff_ninia_log 文件
            if not os.path.exists(ninja_log_path):
                raise FileNotFoundError(f"未找到 .ninja_log 文件: {ninja_log_path}")
            
            # 构建完整的 .diff_ninja_log 文件路径
            diff_ninja_log_path = os.path.join(self._build_dir, ".diff_ninja_log")
            
            with open(ninja_log_path, "r") as ninja_log:
                entries, diff_ninja_log_content = ReadTargets(ninja_log)
                
                with open(diff_ninja_log_path, "w") as diff_ninja_log:
                    diff_ninja_log.write(diff_ninja_log_content)
                
                SummarizeEntries(entries, None)
                
            return diff_ninja_log_path
        except Exception as e:
            self._logger.error(f"创建 .diff_ninja_log 文件失败: {e}")
            return None
            
        
if __name__ == "__main__":
    ninja_util = NinjaUtil(build_dir="/Users/bytedance/Desktop/lark/src/out/release_apollo_arm64", executable="/Users/bytedance/Desktop/lark/depot_tools/ninja")
    # ninja_util.insert_flag_to_ninja_log()
    # print(ninja_util.run_ninja(["-C", ".", "lark"]))
    ninja_util.get_diff_ninja_log()