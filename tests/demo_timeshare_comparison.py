#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分时图优化效果对比演示

生成优化前后的对比图，直观展示改进效果
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def generate_sample_data():
    """生成模拟的分时数据"""
    # 模拟一天的交易数据（上午+下午）
    # 上午：9:30-11:30 (120分钟)
    # 下午：13:00-15:00 (120分钟)
    
    np.random.seed(42)
    
    # 优化前：每5分钟一个点
    n_sparse = 48  # 240分钟 / 5分钟
    x_sparse = np.arange(n_sparse)
    
    # 生成价格走势（带趋势和随机波动）
    trend = np.linspace(0, 2, n_sparse)
    noise = np.random.randn(n_sparse) * 0.5
    y_sparse = 100 + trend + noise
    
    # 优化后：每1分钟一个点
    n_dense = 240
    x_dense = np.arange(n_dense)
    
    # 插值生成密集数据
    x_interp = np.linspace(0, n_sparse-1, n_dense)
    spl = make_interp_spline(x_sparse, y_sparse, k=3)
    y_dense = spl(x_interp)
    
    # 添加更细微的波动
    y_dense += np.random.randn(n_dense) * 0.1
    
    return x_sparse, y_sparse, x_dense, y_dense


def plot_comparison():
    """绘制对比图"""
    x_sparse, y_sparse, x_dense, y_dense = generate_sample_data()
    
    # 创建大图
    fig = plt.figure(figsize=(16, 10))
    
    # 标题
    fig.suptitle('分时图优化效果对比', fontsize=20, fontweight='bold', y=0.98)
    
    # ========== 优化前 ==========
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(x_sparse, y_sparse, 'o-', linewidth=1.5, markersize=6, 
             color='#2196F3', alpha=0.8)
    ax1.set_title('优化前：稀疏数据点', fontsize=14, fontweight='bold', pad=10)
    ax1.set_xlabel('时间（5分钟间隔）', fontsize=11)
    ax1.set_ylabel('价格（元）', fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.text(0.05, 0.95, f'数据点数: {len(x_sparse)}', 
             transform=ax1.transAxes, fontsize=12, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # ========== 优化后 ==========
    ax2 = plt.subplot(2, 2, 2)
    
    # 使用样条插值生成超平滑曲线
    x_super_smooth = np.linspace(x_dense.min(), x_dense.max(), len(x_dense) * 10)
    spl = make_interp_spline(x_dense, y_dense, k=3)
    y_super_smooth = spl(x_super_smooth)
    
    ax2.plot(x_super_smooth, y_super_smooth, '-', linewidth=2, 
             color='#F44336', alpha=0.9, antialiased=True)
    ax2.plot(x_dense, y_dense, 'o', markersize=2, color='#1976D2', alpha=0.3)
    ax2.set_title('优化后：平滑曲线', fontsize=14, fontweight='bold', pad=10)
    ax2.set_xlabel('时间（1分钟间隔）', fontsize=11)
    ax2.set_ylabel('价格（元）', fontsize=11)
    ax2.grid(True, alpha=0.25, linestyle='--', linewidth=0.5)
    ax2.text(0.05, 0.95, f'数据点数: {len(x_dense)}\n插值点数: {len(x_super_smooth)}', 
             transform=ax2.transAxes, fontsize=12, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # ========== 局部放大对比（优化前）==========
    ax3 = plt.subplot(2, 2, 3)
    zoom_start, zoom_end = 10, 20
    ax3.plot(x_sparse[zoom_start:zoom_end], y_sparse[zoom_start:zoom_end], 
             'o-', linewidth=2, markersize=8, color='#2196F3', alpha=0.8)
    ax3.set_title('局部放大：优化前', fontsize=14, fontweight='bold', pad=10)
    ax3.set_xlabel('时间', fontsize=11)
    ax3.set_ylabel('价格（元）', fontsize=11)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.text(0.5, 0.05, '❌ 明显的折线感', 
             transform=ax3.transAxes, fontsize=13, color='red',
             ha='center', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    # ========== 局部放大对比（优化后）==========
    ax4 = plt.subplot(2, 2, 4)
    zoom_start_dense = zoom_start * 5
    zoom_end_dense = zoom_end * 5
    zoom_start_smooth = zoom_start_dense * 10
    zoom_end_smooth = zoom_end_dense * 10
    
    ax4.plot(x_super_smooth[zoom_start_smooth:zoom_end_smooth], 
             y_super_smooth[zoom_start_smooth:zoom_end_smooth], 
             '-', linewidth=2.5, color='#F44336', alpha=0.9, antialiased=True)
    ax4.plot(x_dense[zoom_start_dense:zoom_end_dense], 
             y_dense[zoom_start_dense:zoom_end_dense], 
             'o', markersize=4, color='#1976D2', alpha=0.5)
    ax4.set_title('局部放大：优化后', fontsize=14, fontweight='bold', pad=10)
    ax4.set_xlabel('时间', fontsize=11)
    ax4.set_ylabel('价格（元）', fontsize=11)
    ax4.grid(True, alpha=0.25, linestyle='--', linewidth=0.5)
    ax4.text(0.5, 0.05, '✅ 平滑流畅的曲线', 
             transform=ax4.transAxes, fontsize=13, color='green',
             ha='center', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # 保存图片
    plt.savefig('timeshare_optimization_comparison.png', dpi=200, bbox_inches='tight')
    print("✅ 对比图已保存: timeshare_optimization_comparison.png")
    
    # 显示图片
    plt.show()


def print_summary():
    """打印优化总结"""
    print("\n" + "=" * 70)
    print("分时图优化总结")
    print("=" * 70)
    print()
    print("📊 数据密度提升：")
    print("   优化前：每5分钟1个点，全天约48个点")
    print("   优化后：每1分钟1个点，全天约240个点")
    print("   提升：5倍数据密度")
    print()
    print("🎨 曲线平滑处理：")
    print("   方法：三次样条插值（scipy.interpolate.make_interp_spline）")
    print("   效果：在原始数据点之间生成10倍密度的插值点")
    print("   结果：从240个点插值到2400个点，曲线极其平滑")
    print()
    print("⚡ 性能优化：")
    print("   - 使用antialiased=True启用抗锯齿")
    print("   - 使用draw_idle()延迟绘制")
    print("   - 缓存机制避免重复计算")
    print("   - 快速更新模式用于自动刷新")
    print()
    print("🎯 视觉优化：")
    print("   - 价格线：2px宽度，更清晰")
    print("   - 均价线：1.5px宽度，橙色更醒目")
    print("   - 填充区域：透明度降至8%，避免遮挡")
    print("   - 网格：0.5px细线，透明度25%")
    print("   - Y轴：自动范围，留5%边距")
    print()
    print("=" * 70)


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("分时图优化效果对比演示")
    print("=" * 70 + "\n")
    
    # 检查依赖
    try:
        import scipy
        print(f"✅ scipy版本: {scipy.__version__}")
    except ImportError:
        print("❌ 需要安装scipy: pip install scipy")
        return
    
    print("\n正在生成对比图...")
    plot_comparison()
    
    print_summary()


if __name__ == '__main__':
    main()
