#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能测试脚本 - 测试200只股票监控性能
"""

import time
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QCoreApplication
from core.quote_manager import QuoteManager


def test_quote_manager(stock_count=200, max_workers=30):
    """测试行情管理器性能"""

    print(f"\n{'='*60}")
    print(f"性能测试: {stock_count}只股票, {max_workers}个并发线程")
    print(f"{'='*60}\n")

    # 创建应用（如果不存在）
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # 创建行情管理器
    manager = QuoteManager(max_workers=max_workers)

    # 生成测试股票代码（使用真实的常见股票）
    test_stocks = []
    
    # 常见的上证股票
    sh_stocks = [
        '600000', '600004', '600009', '600010', '600011', '600015', '600016', '600018',
        '600019', '600028', '600029', '600030', '600031', '600036', '600048', '600050',
        '600104', '600109', '600111', '600115', '600150', '600170', '600177', '600188',
        '600196', '600208', '600219', '600221', '600276', '600297', '600309', '600332',
        '600340', '600346', '600352', '600362', '600369', '600372', '600376', '600383',
        '600406', '600415', '600436', '600438', '600482', '600485', '600487', '600489',
        '600498', '600499', '600516', '600518', '600519', '600522', '600547', '600570',
        '600585', '600588', '600606', '600637', '600660', '600663', '600674', '600690',
        '600703', '600705', '600741', '600745', '600760', '600795', '600809', '600837',
        '600848', '600867', '600886', '600887', '600893', '600900', '600919', '600926',
        '600958', '600999', '601006', '601009', '601012', '601018', '601088', '601098',
        '601111', '601117', '601128', '601138', '601155', '601166', '601169', '601186',
        '601198', '601211', '601216', '601225', '601228', '601229', '601288', '601318',
        '601328', '601336', '601360', '601377', '601390', '601398', '601601', '601628',
        '601633', '601668', '601669', '601688', '601766', '601788', '601800', '601818',
        '601857', '601866', '601872', '601877', '601878', '601881', '601888', '601898',
        '601899', '601901', '601919', '601933', '601939', '601985', '601988', '601989',
        '601990', '601991', '601992', '601995', '601997', '601998'
    ]
    
    # 常见的深圳股票
    sz_stocks = [
        '000001', '000002', '000063', '000066', '000069', '000100', '000157', '000333',
        '000338', '000402', '000413', '000415', '000425', '000503', '000538', '000568',
        '000596', '000625', '000651', '000661', '000671', '000703', '000708', '000709',
        '000725', '000728', '000768', '000776', '000783', '000786', '000792', '000800',
        '000858', '000876', '000895', '000898', '000938', '000959', '000963', '001979',
        '002001', '002007', '002008', '002024', '002027', '002032', '002044', '002049',
        '002050', '002142', '002153', '002230', '002236', '002241', '002252', '002271',
        '002304', '002311', '002352', '002371', '002415', '002422', '002460', '002475',
        '002493', '002508', '002555', '002594', '002601', '002602', '002624', '002648',
        '002714', '002736', '002739', '002797', '002841', '002916', '002938', '002945'
    ]
    
    # 常见的创业板股票
    cy_stocks = [
        '300001', '300002', '300003', '300012', '300014', '300015', '300017', '300024',
        '300027', '300033', '300059', '300070', '300122', '300124', '300136', '300142',
        '300144', '300168', '300207', '300223', '300251', '300274', '300285', '300315',
        '300347', '300408', '300413', '300433', '300450', '300454', '300496', '300498',
        '300502', '300529', '300568', '300595', '300601', '300628', '300661', '300676',
        '300750', '300751', '300759', '300760', '300763', '300896', '300957', '300999'
    ]
    
    # 合并所有股票
    all_stocks = sh_stocks + sz_stocks + cy_stocks
    
    # 根据需要的数量选择
    if stock_count <= len(all_stocks):
        test_stocks = all_stocks[:stock_count]
    else:
        # 如果需要更多，循环使用
        test_stocks = (all_stocks * ((stock_count // len(all_stocks)) + 1))[:stock_count]

    # 统计变量
    results = {
        'total': 0,
        'success': 0,
        'error': 0,
        'start_time': None,
        'end_time': None,
        'completed': False
    }

    def on_quote_updated(quote):
        """行情更新回调"""
        results['total'] += 1
        if quote.get('error'):
            results['error'] += 1
        else:
            results['success'] += 1

    def on_progress(completed, total):
        """进度回调"""
        progress = int(completed / total * 100)
        active = manager.get_active_count()
        if progress % 10 == 0:  # 每10%显示一次
            print(f"进度: {completed}/{total} ({progress}%) - 活跃线程: {active}")

    def on_completed():
        """完成回调"""
        results['end_time'] = time.time()
        elapsed = results['end_time'] - results['start_time']

        print(f"\n{'='*60}")
        print("测试完成!")
        print(f"{'='*60}")
        print(f"总股票数: {results['total']}")
        if results['total'] > 0:
            print(f"成功: {results['success']} ({results['success']/results['total']*100:.1f}%)")
            print(f"失败: {results['error']} ({results['error']/results['total']*100:.1f}%)")
            print(f"总耗时: {elapsed:.2f}秒")
            print(f"平均速度: {results['total']/elapsed:.1f}只/秒")
        print(f"{'='*60}\n")

        results['completed'] = True

    # 连接信号
    manager.quote_updated.connect(on_quote_updated)
    manager.batch_progress.connect(on_progress)
    manager.all_completed.connect(on_completed)

    # 开始测试
    print(f"开始获取 {len(test_stocks)} 只股票行情...\n")
    results['start_time'] = time.time()
    manager.fetch_quotes(test_stocks)

    # 等待完成（最多60秒）
    timeout = 60
    start_wait = time.time()
    while not results['completed'] and (time.time() - start_wait) < timeout:
        QCoreApplication.processEvents()
        time.sleep(0.1)

    if not results['completed']:
        print("⚠️ 测试超时！")

    return results


def benchmark_different_configs():
    """测试不同配置的性能"""

    configs = [
        (50, 20),   # 50只股票, 20线程
        (100, 30),  # 100只股票, 30线程
        (200, 30),  # 200只股票, 30线程
        (200, 40),  # 200只股票, 40线程
    ]

    print("\n" + "="*60)
    print("性能基准测试")
    print("="*60)

    all_results = []

    for stock_count, max_workers in configs:
        print(f"\n测试配置: {stock_count}只股票, {max_workers}个线程")
        input("按回车开始测试...")
        result = test_quote_manager(stock_count, max_workers)
        all_results.append({
            'stocks': stock_count,
            'workers': max_workers,
            'result': result
        })
        time.sleep(2)

    # 打印汇总
    print("\n" + "="*60)
    print("基准测试汇总")
    print("="*60)
    for item in all_results:
        r = item['result']
        if r['total'] > 0 and r['end_time']:
            elapsed = r['end_time'] - r['start_time']
            print(f"{item['stocks']}只/{item['workers']}线程: "
                  f"{elapsed:.2f}秒, "
                  f"成功率{r['success']/r['total']*100:.1f}%")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='性能测试脚本')
    parser.add_argument('--stocks', type=int, default=200, help='股票数量')
    parser.add_argument('--workers', type=int, default=30, help='并发线程数')
    parser.add_argument('--benchmark', action='store_true', help='运行基准测试')

    args = parser.parse_args()

    if args.benchmark:
        benchmark_different_configs()
    else:
        test_quote_manager(args.stocks, args.workers)
        sys.exit(0)

