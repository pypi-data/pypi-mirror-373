import os
from typing import List
from base.file import file_util
from base.git import git_util
from base.log import log_util
import semver # type: ignore

class RepoManager:
    """
    一个用于管理特定 Git 仓库克隆和操作的类。
    在实例化时应指定本地路径和远程仓库地址。
    """
    def __init__(self, local_path, repo_url):
        """
        初始化仓库管理器。
        
        :param local_path: 代码将被克隆到的本地路径。
        :param repo_url: Git 仓库的 URL。
        """
        self.local_path = local_path
        self.repo_url = repo_url
        self.logger = log_util.BccacheLogger(
            name="RepoManagerLog",
            use_console=True
        )      
        
        
        # 必须先确保本地目录存在，然后再创建 GitOperator 实例。
        if not os.path.exists(self.local_path):
            self.logger.info(f"Directory not found. Creating: {self.local_path}")
            file_util.FileUtil.make_directory_exists(self.local_path)
        else:
            self.logger.info(f"Target directory already exists: {self.local_path}")
            
        
        self.git_operator = git_util.GitOperator(self.local_path)

    def CheckoutRepo(self, branch, git_clean_excludes: List = []):
        """
        执行检出和清理仓库的核心逻辑。
        
        Args:
            branch: 需要切换的分支, 可以是分支名或commitId
            git_clean_excludes: 执行 git clean 时需要排除在外的目录/文件
        """

        dotGit = os.path.join(self.local_path, '.git')
        
        if not os.path.exists(dotGit):
            self.logger.error("未找到 git 代码仓, 请检查代码仓路径")
            return False
        
         # delete all of the *.lock files 
        for root, dirs, files in os.walk(dotGit):
            for file in files:
                if file.endswith('.lock'):
                    file_util.FileUtil.remove_file(os.path.join(root, file))

        with file_util.ChangeDirectory(self.local_path):
            # clean repo
            self.git_operator.set_git_config("core.fscache", "true")
            self.git_operator.clean_untracked_files(git_clean_excludes)
            # repo config
            self.git_operator.set_git_config("remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*")
            self.git_operator.set_git_config("remote.origin.url", self.repo_url)
            self.git_operator.prune_remote(remote='origin')
            self.git_operator.fetch(remote='origin')

            if self.git_operator.check_branch_exists(branch):
                commitid = self.git_operator._run_command(['rev-parse', f'origin/{branch}^{{commit}}'])
                # is branch
                self.git_operator.checkout_commit_f(commitid)
                self.git_operator.delete_local_branch(branch)        
                self.git_operator.create_and_checkout_branch(branch, commitid)
                self.git_operator._run_command(['log', '--format=%B', '-n', '1', commitid])
            else:
                # is commitid
                commitid = self.git_operator._run_command(['rev-parse', f'{branch}^{{commit}}'])
                if 'fatal:' in commitid:
                    self.logger.error(f"[CheckoutRepo] 未知或无效的 commit ID: '{branch}'. Git 返回: {commitid.strip()}")
                    return None
                self.git_operator.checkout_commit_f(commitid)
                self.git_operator._run_command(['log', '--format=%B', '-n', '1', commitid])

        return self.git_operator

        

