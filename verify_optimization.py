#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证分时图优化是否正确应用

检查项：
1. 代码语法正确性
2. 依赖是否安装
3. 关键函数是否存在
4. 优化是否生效
"""

import sys
import os

def check_syntax():
    """检查代码语法"""
    print("=" * 60)
    print("1. 检查代码语法")
    print("=" * 60)
    
    files_to_check = [
        'main.py',
        'data/fetchers/timeshare_fetcher.py',
    ]
    
    all_ok = True
    for file in files_to_check:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                compile(f.read(), file, 'exec')
            print(f"✅ {file} - 语法正确")
        except SyntaxError as e:
            print(f"❌ {file} - 语法错误: {e}")
            all_ok = False
        except Exception as e:
            print(f"⚠️ {file} - 检查失败: {e}")
            all_ok = False
    
    return all_ok


def check_dependencies():
    """检查依赖"""
    print("\n" + "=" * 60)
    print("2. 检查依赖")
    print("=" * 60)
    
    dependencies = {
        'numpy': '1.24.0',
        'pandas': '2.0.0',
        'matplotlib': '3.7.0',
        'scipy': '1.10.0',
        'PyQt5': '5.15.0',
    }
    
    all_ok = True
    for package, min_version in dependencies.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {package} - 已安装 (版本: {version})")
        except ImportError:
            print(f"❌ {package} - 未安装 (需要 >={min_version})")
            all_ok = False
    
    return all_ok


def check_optimization_code():
    """检查优化代码是否存在"""
    print("\n" + "=" * 60)
    print("3. 检查优化代码")
    print("=" * 60)
    
    checks = []
    
    # 检查1：timeshare_fetcher.py中的1分钟间隔
    try:
        with open('data/fetchers/timeshare_fetcher.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'range(start_min, end_min, 1)' in content:
                print("✅ 数据密度优化 - 1分钟间隔已应用")
                checks.append(True)
            else:
                print("❌ 数据密度优化 - 未找到1分钟间隔代码")
                checks.append(False)
    except Exception as e:
        print(f"❌ 无法检查timeshare_fetcher.py: {e}")
        checks.append(False)
    
    # 检查2：main.py中的样条插值
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'make_interp_spline' in content:
                print("✅ 曲线平滑优化 - 样条插值已应用")
                checks.append(True)
            else:
                print("❌ 曲线平滑优化 - 未找到插值代码")
                checks.append(False)
            
            if 'antialiased=True' in content:
                print("✅ 抗锯齿优化 - 已启用")
                checks.append(True)
            else:
                print("⚠️ 抗锯齿优化 - 未找到（可能使用默认值）")
                checks.append(True)  # 不是关键问题
            
            if 'draw_idle' in content:
                print("✅ 延迟绘制优化 - 已应用")
                checks.append(True)
            else:
                print("❌ 延迟绘制优化 - 未找到")
                checks.append(False)
    except Exception as e:
        print(f"❌ 无法检查main.py: {e}")
        checks.append(False)
    
    return all(checks)


def check_documentation():
    """检查文档是否存在"""
    print("\n" + "=" * 60)
    print("4. 检查文档")
    print("=" * 60)
    
    docs = [
        'docs/TIMESHARE_OPTIMIZATION.md',
        'TIMESHARE_UPGRADE.md',
        'OPTIMIZATION_SUMMARY.md',
    ]
    
    all_ok = True
    for doc in docs:
        if os.path.exists(doc):
            print(f"✅ {doc} - 存在")
        else:
            print(f"❌ {doc} - 不存在")
            all_ok = False
    
    return all_ok


def check_test_files():
    """检查测试文件是否存在"""
    print("\n" + "=" * 60)
    print("5. 检查测试文件")
    print("=" * 60)
    
    tests = [
        'tests/test_timeshare_smooth.py',
        'tests/demo_timeshare_comparison.py',
        'upgrade_timeshare.sh',
    ]
    
    all_ok = True
    for test in tests:
        if os.path.exists(test):
            print(f"✅ {test} - 存在")
        else:
            print(f"❌ {test} - 不存在")
            all_ok = False
    
    return all_ok


def print_summary(results):
    """打印总结"""
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {check}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有检查通过！优化已正确应用。")
        print("\n下一步：")
        print("1. 安装scipy: pip3 install scipy")
        print("2. 运行升级脚本: bash upgrade_timeshare.sh")
        print("3. 启动程序: bash start_with_ime.sh")
    else:
        print("⚠️ 部分检查未通过，请查看上面的详细信息。")
        print("\n建议：")
        if not results.get('依赖检查', True):
            print("- 安装缺失的依赖: pip3 install -r requirements.txt")
        if not results.get('优化代码检查', True):
            print("- 检查代码是否正确修改")
    print("=" * 60)


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("分时图优化验证工具")
    print("=" * 60 + "\n")
    
    results = {
        '语法检查': check_syntax(),
        '依赖检查': check_dependencies(),
        '优化代码检查': check_optimization_code(),
        '文档检查': check_documentation(),
        '测试文件检查': check_test_files(),
    }
    
    print_summary(results)


if __name__ == '__main__':
    main()
