import os
import blazecache
from pathlib import Path
import subprocess
from base.log import log_util
from business import compilecachesubmit_plugin

# def lark_filter_func(name: str) -> bool:
#     if name.split(".")[-1] in ["stamp", "o", "obj", "lib", "h", "res", "exe", "cc", "pdb", "dll" ,'a' ,'unstripped' ,'dylib' ,'TOC']:
#         if name not in  ["frame.dll.pdb","frame.dll","frame.dll.lib"]:
#             return True

#         # 检查是否为无后缀的 Unix/macOS 可执行文件
#         if os.path.isfile(os.path.join("/Users/bytedance/Desktop/lark/src/out/release_apollo_arm64", name.replace(".unstripped", ""))):
#             return True
#         elif name.endswith("ids"): #gen/tools/gritsettings/default_resource_ids should be taken in account
#             return True
        
#         return False

def build_aha_electron(repo_dir: str):
    # eval_fnm_cmd = "" if sys.platform == 'win32' else 'eval $(fnm env) && fnm use 20 &&'
    cmd = 'python3 aha/build/electron_build.py -m Release --target_cpu arm64 --with-dist-zip'
    result = subprocess.run(cmd, shell=True, check=True, cwd=repo_dir)
    return True
    

if __name__ == "__main__":
    electron_repo_code_dir = {
        "aha-electron": "/Users/bytedance/Desktop/aha-electron/aha-electron",
    }
    electron_feature_branch = {
        "aha-electron": "c2bb3836799b0de8fa41cb41d48c6d0b464b7290"
    }
    blaze_cache = blazecache.BlazeCache(product_name="aha-electron", build_dir="/Users/bytedance/Desktop/aha-electron/aha-electron",
                                        local_repo_dir=electron_repo_code_dir, os_type="Darwin",
                                        task_type="cache_generator_task", branch_type="main", machine_id="123456",
                                        ninja_exe_path="/Users/bytedance/Desktop/aha-electron/depot_tools/ninja",
                                        mr_target_branch="v34.5.1", feature_branch=electron_feature_branch, p4_client="test_blazecache_client_electron",
                                        fallback_branch=None, product_tos_path="product_config/aha-electron/product_config.json")
    
    blaze_cache.run_compile_cache_submit_plugin(build_executor=lambda: build_aha_electron(repo_dir="/Users/bytedance/Desktop/aha-electron/aha-electron"),
                                                p4_ignore_url="https://tosv.byted.org/obj/kernel-perf-benchmark-cn/p4ignore/p4_ignore",
                                                mr_target_branch=electron_feature_branch, filter_func=None, p4_submit_label="init aha-electron")