# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-04 11:13
# @Author : 毛鹏
import time
import unittest
import os
import shutil
from dulwich.repo import Repo
from mangotools.mangos import GitRepoOperator


class Log():
    def info(self, msg):
        print(msg)

    def debug(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def critical(self, msg):
        print(msg)


log = Log()


class TestGitOperations(unittest.TestCase):
    REPO_URL = "https://gitee.com/mao-peng/MangoPytest.git"
    path = 'D:\code\mango_tools'
    TEST_REPO_DIR = os.path.join(path, "mango_pytest")
    USERNAME = 'mao-peng'
    PASSWORD = 'mP729164035'

    @classmethod
    def setUpClass(cls):
        """创建测试用的GitRepoOperator实例"""
        cls.git_operator = GitRepoOperator(
            cls.REPO_URL,
            cls.path,
            log,
            username=cls.USERNAME,
            password=cls.PASSWORD,
        )

        # 确保测试目录不存在
        if os.path.exists(cls.TEST_REPO_DIR):
            shutil.rmtree(cls.TEST_REPO_DIR)

    @classmethod
    def tearDownClass(cls):
        """清理测试创建的目录"""
        pass

    def test_01_clone_repository(self):
        """测试仓库克隆功能"""
        self.git_operator.clone(force_clone=False)

        self.assertTrue(os.path.exists(self.TEST_REPO_DIR))
        self.assertTrue(os.path.exists(os.path.join(self.TEST_REPO_DIR, '.git')))

        repo = Repo(self.TEST_REPO_DIR)
        config = repo.get_config()
        remote_url = config.get(('remote', 'origin'), 'url')
        print(remote_url)


    def test_02_pull_updates(self):
        """测试拉取更新功能"""
        if not os.path.exists(self.TEST_REPO_DIR):
            self.git_operator.clone()
        self.git_operator.pull(accept_remote=True)

        repo_info = self.git_operator.get_repo_info()
        print(repo_info)

    def test_03_push_changes(self):
        """测试推送更改功能"""
        test_file = os.path.join(self.TEST_REPO_DIR, "README.md")
        self.git_operator.clone()
        if not os.path.exists(test_file):
            with open(test_file, 'w') as f:
                f.write("This is a test file for Git operations\n")
        else:
            with open(test_file, 'a') as f:
                f.write("1\n")

        self.git_operator.push()

        repo_info = self.git_operator.get_repo_info()
        print(repo_info['is_dirty'])

        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("1", content)


    def test_04_get_repo_info(self):
        """测试获取仓库信息功能"""
        repo_info = self.git_operator.get_repo_info()

        # 验证返回的信息结构
        self.assertIsInstance(repo_info, dict)
        self.assertIn('active_branch', repo_info)
        self.assertIn('commit_hash', repo_info)
        self.assertIn('is_dirty', repo_info)
        self.assertIn('remote_url', repo_info)

        # 打印仓库信息（与示例中的格式一致）
        print("\n📊 仓库信息:")
        print(f"   当前分支: {repo_info['active_branch']}")
        print(f"   最新提交: {repo_info['commit_hash']}")
        print(f"   是否有未提交更改: {'是' if repo_info['is_dirty'] else '否'}")
        print(f"   远程仓库: {repo_info['remote_url']}")



if __name__ == '__main__':
    unittest.main(verbosity=2)
