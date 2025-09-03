import blazecache.blazecache as blazecache

if __name__ == "__main__":
    lark_repo_code_dir = {
        "aha": "/Users/bytedance/Desktop/lark/src",
        "iron": "/Users/bytedance/Desktop/lark/src/aha/iron"
    }
    lark_feature_branch = {
        "aha": "feature_permissionquery",
        "iron": "dev"
    }
    fallback_branch = {
        "aha": "hkx/test_blazecache",
        "iron": "hkx/test_blazecache"
    }
    mr_target_branch = {
        "aha": "m131",
        "iron": "dev"
    }
    bccache = blazecache.BlazeCache(product_name="lark", build_dir="/Users/bytedance/Desktop/lark/src/",
                                    local_repo_dir=lark_repo_code_dir, os_type="darwin", branch_type="main", task_type="ci_check_task",
                                    machine_id="123456", ninja_exe_path="/Users/bytedance/Desktop/lark/depot_tools/ninja",
                                    mr_target_branch=mr_target_branch, feature_branch=lark_feature_branch, p4_client="test-ci-check", fallback_branch=fallback_branch, product_tos_path="product_config/lark/product_config.json")
    bccache.run_precompile_plugin(mr_id="1234")
    # print(bccache.run_postcompile_plugin())