import pytest
import sys
import os

# 确保可以导入rpaworkflow包
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 测试会话开始前的钩子
@pytest.fixture(scope="session", autouse=True)
def setup_test_session():
    """测试会话开始前的设置"""
    print("\n开始测试会话...")
    yield
    print("\n测试会话结束...")

# 每个测试函数前的钩子
@pytest.fixture(autouse=True)
def setup_test_function():
    """每个测试函数前的设置"""
    yield