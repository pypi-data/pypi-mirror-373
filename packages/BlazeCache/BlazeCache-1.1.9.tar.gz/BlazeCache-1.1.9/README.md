# BlazeCache
BlazeCache是一款帮助业务精细化管理编译缓存的套件，可以精准命中缓存，提升编译效率

# 开发指南
项目使用 setup_tools 打包，指定 src 为根目录, 初始化项目时在根目录使用 `pip install -e .` 安装包
随后就可以自由地调包了

# product_config
product_config 是项目的配置文件，由于项目需要支持不同的产品，因此需要将部分固定的配置导入配置文件中，针对不同的项目拉取对应的配置文件，解析并配置对应的参数。
## 配置文件内容格式
具体格式可以参考 src/module/config/example_product_config.json 文件，这里着重介绍 repo_info 以及 p4_config
### repo_info
repo_info 必须提供一个列表，保存所有仓库信息，例如 lark 需要提供 aha&iron 的信息。需要提供仓库远端 url，用于下载代码仓。
### p4_config
p4_config 是 p4 的初始化配置信息，考虑到兼容 Lark 与其他产品，p4 服务器的区分方式是：操作系统平台->任务类型->分支类型（主干/release）
因为在 Lark 这边，不同的操作系统（Mac、Win、Linux）、任务类型（ci_check_task、cache_generator_task）、分支类型（主干、release）使用的 P4 服务器都是不一样的。所以需要使用这种方式进行区分。
**p4参数说明**
1. WORKDIR：p4 的工作路径，用于配置 p4.cwd，该参数填写相对路径，相对于代码仓根目录的相对路径，例如 lark 代码仓是 src，编译缓存位于 src/out/release_apollo_arm64，那么该参数填写"out/release_apollo_arm64"
2. LABEL_REGEX：填写正则表达式，用于从 label 中提取 commitID，规定 p4 label 中必须包含 commitID，但由于不同产品的 label 组织形式不同，所以根据配置不同的正则表达式，来提取 commitID。
3. DELETE_CLIENT：是否需要在每次 sync 后删除 p4 client，填写 bool 值。例如 Lark 对于主干是不需要每次 sync 都删除 client 的，而对于 release 版本，需要每次 sync 都删除 client。如果每次 sync 删除 client，则必须使用 sync -f 全量拉取缓存。
## product_config.json 本地存储位置
1. Mac：~/Library/Application\ Support/BlazeCache_tmp/product_config/{product_name}/product_config.json
2. Win：%AppData%/BlazeCache_tmp/product_config/{product_name}/product_config.json
3. Linux：~/./config/BlazeCache_tmp/product_config/{product_name}/product_config.json

# .diff_ninja_log
## 作用
在 BlazeCache 中，ci_check_task 和 cache_generator_task 都需要使用到 .diff_ninja_log 文件，这里会记录上一次编译中，实际编译的 target 条目。
但是二者利用 .diff_ninja_log 的方式不一样。
1. ci_check_task：使用 .diff_ninja_log 是获取上一次编译的 target，将其 edit -f 加入到 changelist 中，执行 p4 revert，即清理上一次编译遗留下来的缓存，目的是不对本次缓存进行干扰。
2. cache_generator_task：使用 .diff_ninja_log 获取上一次编译的 target，由于 p4 reconcile 对 md5 进行识别，对于某些文件 md5 不变，但是时间戳改变的情况，这部分无法被 p4 reconcile 识别
所以无法添加到 changelist 中，也就不会被上传到缓存服务器中。因此需要测速任务编译完后，从 .diff_ninja_log 中将其 edit -f 添加到 changelist，最后 submit 到远端，从而保证缓存的完整性。
## 创建&上传 .diff_ninja_log
请使用 BlazeCache.create_diff_ninja_log 函数创建并上传 .diff_ninja_log，该函数会先获取上一次上传的 .diff_ninja_log 的 id，然后 id 自增，创建新的 .diff_ninja_log 文件后，赋予新的 id 值并上传 tos。
**使用姿势**
1. ci_check_task：执行流程大致是 repo准备->p4_manager->提醒用户编译。所以对于 ci 检查任务，创建&上传 .diff_ninja_log 的时机是用户编译完以后，调用 BlazeCache.create_diff_ninja_log 函数创建并上传。
2. cache_generator_task：执行流程大致是 repo准备->编译->p4_manager。所以对于做缓存任务，创建&上传 .diff_ninja_log 的时机是编译完以后，调用 BlazeCache.create_diff_ninja_log，再将 .diff_ninja_log 传递给 p4_manager 执行 p4 操作。
## 获取 .diff_ninja_log
请使用 BlazeCache.get_diff_ninja_log 获取 .diff_ninja_log 文件，该函数会先在本地查找是否已经存在，若不存在会从 tos 下载
### 本地存储路径
1. Mac：~/Library/Application\ Support/BlazeCache_tmp/diff_ninja_log/{product_name}/{os_type}/{job_type}/{branch_type}/{machine_id}/{id}/.diff_ninja_log
2. Win：%AppData%/BlazeCache_tmp/diff_ninja_log/{product_name}/{os_type}/{job_type}/{branch_type}/{machine_id}/{id}/.diff_ninja_log
3. Linux：~/./config/BlazeCache_tmp/diff_ninja_log/{product_name}/{os_type}/{job_type}/{branch_type}/{machine_id}/{id}/.diff_ninja_log