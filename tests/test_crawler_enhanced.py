#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版爬虫功能
"""

from data.fetchers.stock_info_crawler import StockInfoCrawler


def test_crawler():
    """测试爬虫功能"""
    print("=" * 60)
    print("测试增强版股票信息爬虫")
    print("=" * 60)
    
    crawler = StockInfoCrawler()
    
    # 测试股票代码
    test_codes = ['600519', '000001', '002342']
    
    for code in test_codes:
        print(f"\n\n{'=' * 60}")
        print(f"测试股票: {code}")
        print('=' * 60)
        
        try:
            info = crawler.get_stock_info(code)
            
            # 统计信息
            print(f"\n获取到的信息类型：")
            print(f"- 公司信息: {len(info.get('company_info', {}))} 项")
            print(f"- 财务数据: {len(info.get('financial', {}))} 项")
            print(f"- 公告: {len(info.get('announcements', []))} 条")
            print(f"- 新闻: {len(info.get('news', []))} 条")
            print(f"- 研报: {len(info.get('research_reports', []))} 条")
            print(f"- 资金流向: {len(info.get('capital_flow', {}))} 项")
            print(f"- 股东信息: {len(info.get('holder_info', {}))} 项")
            
            # 显示详细信息
            if info.get('company_info'):
                print(f"\n公司信息示例：")
                company = info['company_info']
                if company.get('name'):
                    print(f"  名称: {company['name']}")
                if company.get('industry'):
                    print(f"  行业: {company['industry']}")
            
            if info.get('financial'):
                print(f"\n财务数据示例：")
                fin = info['financial']
                if fin.get('pe_ratio'):
                    print(f"  PE: {fin['pe_ratio']:.2f}")
                if fin.get('total_market_cap'):
                    print(f"  总市值: {fin['total_market_cap']:.2f}亿")
            
            if info.get('capital_flow'):
                print(f"\n资金流向示例：")
                flow = info['capital_flow']
                if flow.get('main_net_inflow') is not None:
                    print(f"  主力净流入: {flow['main_net_inflow']:.2f}万")
            
            # 格式化输出
            print(f"\n格式化输出（前1000字符）：")
            formatted = crawler.format_info(info)
            print(formatted[:1000])
            print("...")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    test_crawler()
