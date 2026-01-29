#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分时图平滑效果测试

测试内容：
1. 数据插值效果
2. 绘图性能
3. 平滑度对比
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import time


def test_interpolation():
    """测试插值效果"""
    print("=" * 60)
    print("测试1: 数据插值效果")
    print("=" * 60)
    
    # 生成模拟数据（稀疏）
    x_sparse = np.array([0, 10, 20, 30, 40, 50])
    y_sparse = np.array([100, 102, 98, 103, 99, 101])
    
    print(f"原始数据点数: {len(x_sparse)}")
    
    # 插值生成密集数据
    x_dense = np.linspace(x_sparse.min(), x_sparse.max(), len(x_sparse) * 10)
    spl = make_interp_spline(x_sparse, y_sparse, k=3)
    y_dense = spl(x_dense)
    
    print(f"插值后数据点数: {len(x_dense)}")
    print(f"密度提升: {len(x_dense) / len(x_sparse):.1f}x")
    
    # 可视化对比
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(x_sparse, y_sparse, 'o-', label='原始数据', linewidth=1.5, markersize=8)
    plt.title('优化前：稀疏数据点')
    plt.xlabel('时间')
    plt.ylabel('价格')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(x_dense, y_dense, '-', label='插值平滑', linewidth=2, color='red')
    plt.plot(x_sparse, y_sparse, 'o', label='原始点', markersize=6, color='blue')
    plt.title('优化后：平滑曲线')
    plt.xlabel('时间')
    plt.ylabel('价格')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('timeshare_interpolation_test.png', dpi=150)
    print("✅ 对比图已保存: timeshare_interpolation_test.png")
    plt.close()


def test_performance():
    """测试绘图性能"""
    print("\n" + "=" * 60)
    print("测试2: 绘图性能")
    print("=" * 60)
    
    # 生成模拟分时数据
    n_points = 240  # 全天分钟数
    x = np.arange(n_points)
    y = 100 + np.cumsum(np.random.randn(n_points) * 0.5)
    
    # 测试原始绘制
    fig, ax = plt.subplots(figsize=(10, 6))
    
    start = time.time()
    ax.plot(x, y, linewidth=1.5)
    fig.canvas.draw()
    time_original = time.time() - start
    
    plt.close(fig)
    
    # 测试插值绘制
    x_smooth = np.linspace(x.min(), x.max(), len(x) * 10)
    spl = make_interp_spline(x, y, k=3)
    y_smooth = spl(x_smooth)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    start = time.time()
    ax.plot(x_smooth, y_smooth, linewidth=2, antialiased=True)
    fig.canvas.draw()
    time_smooth = time.time() - start
    
    plt.close(fig)
    
    print(f"原始绘制耗时: {time_original*1000:.2f}ms")
    print(f"平滑绘制耗时: {time_smooth*1000:.2f}ms")
    print(f"性能差异: {(time_smooth/time_original - 1)*100:+.1f}%")
    
    if time_smooth < time_original * 1.5:
        print("✅ 性能影响可接受（<50%增加）")
    else:
        print("⚠️ 性能影响较大，需要进一步优化")


def test_real_timeshare_data():
    """测试真实分时数据"""
    print("\n" + "=" * 60)
    print("测试3: 真实分时数据平滑效果")
    print("=" * 60)
    
    try:
        from data.fetchers.timeshare_fetcher import TimeshareFetcher
        
        fetcher = TimeshareFetcher(verbose=True)
        
        # 测试上证指数
        print("\n获取上证指数分时数据...")
        df = fetcher.get_timeshare_data('999999')
        
        if df is not None and not df.empty:
            print(f"✅ 获取成功，数据点数: {len(df)}")
            
            # 原始数据
            x = np.arange(len(df))
            y = df['price'].values
            
            # 插值平滑
            if len(df) > 3:
                x_smooth = np.linspace(x.min(), x.max(), len(x) * 10)
                spl = make_interp_spline(x, y, k=3)
                y_smooth = spl(x_smooth)
                
                # 可视化
                plt.figure(figsize=(14, 6))
                
                plt.subplot(1, 2, 1)
                plt.plot(x, y, 'o-', linewidth=1.5, markersize=4)
                plt.title(f'原始数据 ({len(df)}个点)')
                plt.xlabel('时间索引')
                plt.ylabel('价格')
                plt.grid(True, alpha=0.3)
                
                plt.subplot(1, 2, 2)
                plt.plot(x_smooth, y_smooth, '-', linewidth=2, color='red', antialiased=True)
                plt.plot(x, y, 'o', markersize=3, color='blue', alpha=0.5)
                plt.title(f'平滑曲线 ({len(x_smooth)}个点)')
                plt.xlabel('时间索引')
                plt.ylabel('价格')
                plt.grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.savefig('timeshare_real_data_test.png', dpi=150)
                print("✅ 真实数据对比图已保存: timeshare_real_data_test.png")
                plt.close()
            else:
                print("⚠️ 数据点太少，无法进行插值")
        else:
            print("❌ 获取数据失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_smoothness_metrics():
    """测试平滑度指标"""
    print("\n" + "=" * 60)
    print("测试4: 平滑度量化分析")
    print("=" * 60)
    
    # 生成测试数据
    x = np.linspace(0, 10, 50)
    y = np.sin(x) + np.random.randn(50) * 0.1
    
    # 计算原始数据的二阶导数（曲率）
    dy_original = np.diff(y)
    ddy_original = np.diff(dy_original)
    curvature_original = np.abs(ddy_original).mean()
    
    # 插值平滑
    x_smooth = np.linspace(x.min(), x.max(), len(x) * 10)
    spl = make_interp_spline(x, y, k=3)
    y_smooth = spl(x_smooth)
    
    # 计算平滑数据的二阶导数
    dy_smooth = np.diff(y_smooth)
    ddy_smooth = np.diff(dy_smooth)
    curvature_smooth = np.abs(ddy_smooth).mean()
    
    print(f"原始数据平均曲率: {curvature_original:.6f}")
    print(f"平滑数据平均曲率: {curvature_smooth:.6f}")
    print(f"平滑度提升: {(1 - curvature_smooth/curvature_original)*100:.1f}%")
    
    if curvature_smooth < curvature_original:
        print("✅ 曲线更加平滑")
    else:
        print("⚠️ 平滑效果不明显")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("分时图平滑优化测试")
    print("=" * 60 + "\n")
    
    # 检查scipy是否安装
    try:
        import scipy
        print(f"✅ scipy版本: {scipy.__version__}")
    except ImportError:
        print("❌ scipy未安装，请运行: pip install scipy")
        return
    
    # 运行测试
    test_interpolation()
    test_performance()
    test_smoothness_metrics()
    test_real_timeshare_data()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n生成的文件：")
    print("- timeshare_interpolation_test.png  # 插值效果对比")
    print("- timeshare_real_data_test.png      # 真实数据效果")


if __name__ == '__main__':
    main()
