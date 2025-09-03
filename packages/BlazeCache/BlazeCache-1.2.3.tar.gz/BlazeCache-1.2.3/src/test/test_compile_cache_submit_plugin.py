import os
import blazecache
from pathlib import Path
import subprocess
from base.log import log_util
from business import compilecachesubmit_plugin

def lark_filter_func(name: str) -> bool:
    if name.split(".")[-1] in ["stamp", "o", "obj", "lib", "h", "res", "exe", "cc", "pdb", "dll" ,'a' ,'unstripped' ,'dylib' ,'TOC']:
        if name not in  ["frame.dll.pdb","frame.dll","frame.dll.lib"]:
            return True

        # 检查是否为无后缀的 Unix/macOS 可执行文件
        if os.path.isfile(os.path.join("/Users/bytedance/Desktop/lark/src/out/release_apollo_arm64", name.replace(".unstripped", ""))):
            return True
        elif name.endswith("ids"): #gen/tools/gritsettings/default_resource_ids should be taken in account
            return True
        
        return False

def run_lark_build(root_dir: str, sdk_version: str = "7.42.0", logger = None) -> bool:
    """
    执行 Lark 项目构建，等效于提供的 Bash 脚本
    
    Args:
        root_dir: lark代码根目录, 一般为 src 的父级目录
        sdk_version: SDK 版本号，默认为 7.42.0
        logger: 日志记录器
    
    Returns:
        构建成功返回 True, 失败返回 False
    """
    # 初始化日志
    if logger is None:
        
        logger = log_util.BccacheLogger(name="lark_build")
    
    try:
        
        # 定义路径变量（等效于 Bash 中的 src 和 depot_tools）
        src_dir = f"{root_dir}/src"
        depot_tools_dir = f"{root_dir}/depot_tools"
        src_dir = Path(src_dir)
        depot_tools_dir = Path(depot_tools_dir)
        
        # 验证目录是否存在
        if not src_dir.exists():
            logger.error(f"源目录不存在: {src_dir}")
            return False
        if not depot_tools_dir.exists():
            logger.error(f"depot_tools 目录不存在: {depot_tools_dir}")
            return False
        
        # 设置环境变量 PATH（添加 depot_tools 目录）
        original_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{original_path}:{depot_tools_dir}"
        logger.info(f"已将 depot_tools 添加到 PATH: {depot_tools_dir}")
        
        # 切换到构建目录（等效于 cd $src/aha/build）
        build_dir = src_dir / "aha" / "build"
        if not build_dir.exists():
            logger.error(f"构建目录不存在: {build_dir}")
            return False
        os.chdir(build_dir)
        logger.info(f"已切换到构建目录: {build_dir}")
        
        # 构建命令参数
        command = [
            "python3",
            "lark_build.py",
            "-t", "lark",
            "-x", "3",
            "-iron",
            "-m", "release",
            "-c", sdk_version,
            "--use-aha-compile-cache",
            "-a", 'mac_sdk_path="/Users/bytedance/Desktop/lark/MacOSX15.1.sdk"',
            "-a", "strip_absolute_paths_from_debug_symbols=false",
            "-a", "enable_precompiled_headers=false"
        ]
        
        # 执行构建命令
        logger.info(f"开始执行构建命令: {' '.join(command)}")
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        # 输出命令执行结果
        logger.info(f"构建成功！输出:\n{result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"构建命令执行失败！返回码: {e.returncode}")
        logger.error(f"错误输出:\n{e.stderr}")
        return False
    except Exception as e:
        logger.error(f"构建过程中发生错误: {str(e)}")
        return False
    finally:
        # 恢复原始 PATH（可选，根据需求决定是否恢复）
        # os.environ["PATH"] = original_path
        pass
    

if __name__ == "__main__":
    lark_repo_code_dir = {
        "aha": "/Users/bytedance/Desktop/lark/src",
        "iron": "/Users/bytedance/Desktop/lark/src/aha/iron"
    }
    lark_feature_branch = {
        "aha": "m131",
        "iron": "dev"
    }
    fallback_branch = {
        "aha": "test_blazecache",
        "iron": "test_blazecache_iron"
    }
    blaze_cache = blazecache.BlazeCache(product_name="lark", build_dir="/Users/bytedance/Desktop/lark/src",
                                        local_repo_dir=lark_repo_code_dir, os_type="Darwin",
                                        task_type="cache_generator_task", branch_type="main", machine_id="123456",
                                        ninja_exe_path="/Users/bytedance/Desktop/lark/depot_tools/ninja",
                                        mr_target_branch="m131", feature_branch=lark_feature_branch, p4_client="test_blazecache_client",
                                        fallback_branch=fallback_branch, product_tos_path="product_config/lark/product_config.json")
    
    blaze_cache.run_compile_cache_submit_plugin(build_executor=lambda: run_lark_build(root_dir="/Users/bytedance/Desktop/lark"),
                                                p4_ignore_url="https://voffline.byted.org/download/tos/schedule/mybucket/self_signed_cache/bits/mac/.p4ignore",
                                                mr_target_branch=lark_feature_branch, filter_func=lark_filter_func, p4_submit_label="test_blazecache",
                                                modify_timestamp=True)