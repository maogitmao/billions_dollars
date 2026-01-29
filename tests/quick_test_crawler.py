#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试爬虫增强功能
"""

from data.fetchers.stock_info_crawler import StockInfoCrawler


def quick_test():
    """快速测试"""
    print("🚀 快速测试爬虫增强功能\n")
    
    crawler = StockInfoCrawler()
    
    # 测试一只股票
    code = '600519'
    print(f"测试股票: {code} (贵州茅台)\n")
    
    try:
        info = crawler.get_stock_info(code)
        
        # 检查各项功能
        checks = {
            '公司信息': len(info.get('company_info', {})) > 0,
            '财务数据': len(info.get('financial', {})) > 0,
            '公告信息': len(info.get('announcements', [])) > 0,
            '新闻资讯': len(info.get('news', [])) > 0,
            '研究报告': len(info.get('research_reports', [])) > 0,
            '资金流向': len(info.get('capital_flow', {})) > 0,
            '股东信息': len(info.get('holder_info', {})) > 0,
        }
        
        print("功能检查结果：")
        for name, status in checks.items():
            icon = "✅" if status else "❌"
            count = ""
            if name == '公司信息':
                count = f"({len(info.get('company_info', {}))}项)"
            elif name == '财务数据':
                count = f"({len(info.get('financial', {}))}项)"
            elif name == '公告信息':
                count = f"({len(info.get('announcements', []))}条)"
            elif name == '新闻资讯':
                count = f"({len(info.get('news', []))}条)"
            elif name == '研究报告':
                count = f"({len(info.get('research_reports', []))}条)"
            elif name == '资金流向':
                count = f"({len(info.get('capital_flow', {}))}项)"
            elif name == '股东信息':
                count = f"({len(info.get('holder_info', {}))}项)"
            
            print(f"  {icon} {name}: {count}")
        
        # 显示详细示例
        print("\n详细信息示例：")
        
        if info.get('company_info'):
            print("\n📌 公司信息：")
            company = info['company_info']
            for key, value in company.items():
                print(f"  - {key}: {value}")
        
        if info.get('financial'):
            print("\n📌 财务数据（前5项）：")
            fin = info['financial']
            for i, (key, value) in enumerate(list(fin.items())[:5]):
                print(f"  - {key}: {value}")
        
        if info.get('capital_flow'):
            print("\n📌 资金流向：")
            flow = info['capital_flow']
            for key, value in flow.items():
                print(f"  - {key}: {value:.2f}万元")
        
        if info.get('research_reports'):
            print(f"\n📌 研究报告（共{len(info['research_reports'])}条）：")
            for i, report in enumerate(info['research_reports'][:3], 1):
                print(f"  {i}. {report['title'][:50]}...")
                print(f"     机构: {report['org']}, 评级: {report['rating']}")
        
        # 统计总结
        print("\n" + "=" * 60)
        print("📊 数据统计总结：")
        total_items = (
            len(info.get('company_info', {})) +
            len(info.get('financial', {})) +
            len(info.get('announcements', [])) +
            len(info.get('news', [])) +
            len(info.get('research_reports', [])) +
            len(info.get('capital_flow', {})) +
            len(info.get('holder_info', {}))
        )
        print(f"  总计获取: {total_items} 项数据")
        print(f"  数据完整度: {sum(checks.values())}/{len(checks)} = {sum(checks.values())/len(checks)*100:.1f}%")
        
        success_rate = sum(checks.values()) / len(checks) * 100
        if success_rate >= 80:
            print(f"\n✅ 测试通过！数据获取成功率: {success_rate:.1f}%")
        elif success_rate >= 50:
            print(f"\n⚠️ 部分成功。数据获取成功率: {success_rate:.1f}%")
            print("   提示：部分数据源可能暂时不可用，这是正常现象")
        else:
            print(f"\n❌ 测试失败。数据获取成功率: {success_rate:.1f}%")
            print("   提示：请检查网络连接")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    quick_test()
