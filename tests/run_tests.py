"""测试运行器"""

import sys
import unittest
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.config import TestConfig
from tests.utils import FileTestHelper


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Expert Potato E2E 测试套件")
    print("=" * 60)
    
    # 确保测试环境
    TestConfig.ensure_test_dirs()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试模块
    test_modules = [
        'tests.test_components',
        'tests.test_e2e_core_flow',
    ]
    
    for module_name in test_modules:
        try:
            module_suite = loader.loadTestsFromName(module_name)
            suite.addTest(module_suite)
            print(f"✓ 已加载测试模块: {module_name}")
        except Exception as e:
            print(f"✗ 加载测试模块失败: {module_name}, 错误: {e}")
    
    # 运行测试
    print("\n" + "-" * 60)
    print("开始运行测试...")
    print("-" * 60)
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    print(f"运行时间: {end_time - start_time:.2f} 秒")
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # 清理测试文件
    try:
        FileTestHelper.cleanup_test_files()
        print("\n✓ 测试文件清理完成")
    except Exception as e:
        print(f"\n⚠ 测试文件清理失败: {e}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n测试结果: {'通过' if success else '失败'}")
    print("=" * 60)
    
    return success


def run_e2e_tests_only():
    """只运行E2E测试"""
    print("=" * 60)
    print("Expert Potato E2E 核心流程测试")
    print("=" * 60)
    
    # 确保测试环境
    TestConfig.ensure_test_dirs()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_e2e_core_flow')
    
    # 运行测试
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    print(f"\nE2E测试完成，耗时: {end_time - start_time:.2f} 秒")
    return len(result.failures) == 0 and len(result.errors) == 0


def run_component_tests_only():
    """只运行组件测试"""
    print("=" * 60)
    print("Expert Potato 组件单元测试")
    print("=" * 60)
    
    # 确保测试环境
    TestConfig.ensure_test_dirs()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_components')
    
    # 运行测试
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    print(f"\n组件测试完成，耗时: {end_time - start_time:.2f} 秒")
    return len(result.failures) == 0 and len(result.errors) == 0


def main():
    """主函数"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == 'e2e':
            success = run_e2e_tests_only()
        elif test_type == 'component':
            success = run_component_tests_only()
        elif test_type == 'all':
            success = run_all_tests()
        else:
            print(f"未知的测试类型: {test_type}")
            print("可用选项: all, e2e, component")
            sys.exit(1)
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()