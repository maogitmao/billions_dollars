#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票信息爬虫 - 获取公告、新闻、财务数据等详细信息

数据源：
- 东方财富网（公告、新闻、财务数据）
- 新浪财经（实时资讯）
- 同花顺（研报）
"""

import requests
from datetime import datetime
import json
import re


class StockInfoCrawler:
    """股票信息爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://www.eastmoney.com/'
        })
    
    def get_stock_info(self, stock_code):
        """
        获取股票的所有详细信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            dict: 包含公告、新闻、财务等详细信息
        """
        result = {
            'code': stock_code,
            'announcements': [],
            'news': [],
            'financial': {},
            'company_info': {},
            'research_reports': [],
            'capital_flow': {},
            'holder_info': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 获取公司基本信息
        try:
            company_info = self.get_company_info(stock_code)
            result['company_info'] = company_info
        except Exception as e:
            result['company_info_error'] = str(e)
        
        # 获取公告（详细版）
        try:
            announcements = self.get_announcements_detailed(stock_code)
            result['announcements'] = announcements
        except Exception as e:
            result['announcements_error'] = str(e)
        
        # 获取新闻（详细版）
        try:
            news = self.get_news_detailed(stock_code)
            result['news'] = news
        except Exception as e:
            result['news_error'] = str(e)
        
        # 获取财务数据（增强版）
        try:
            financial = self.get_financial_data_enhanced(stock_code)
            result['financial'] = financial
        except Exception as e:
            result['financial_error'] = str(e)
        
        # 获取研报信息
        try:
            research = self.get_research_reports(stock_code)
            result['research_reports'] = research
        except Exception as e:
            result['research_error'] = str(e)
        
        # 获取资金流向
        try:
            capital_flow = self.get_capital_flow(stock_code)
            result['capital_flow'] = capital_flow
        except Exception as e:
            result['capital_flow_error'] = str(e)
        
        # 获取股东信息
        try:
            holder_info = self.get_holder_info(stock_code)
            result['holder_info'] = holder_info
        except Exception as e:
            result['holder_error'] = str(e)
        
        # 获取龙虎榜数据
        try:
            dragon_tiger = self.get_dragon_tiger_list(stock_code)
            result['dragon_tiger'] = dragon_tiger
        except Exception as e:
            result['dragon_tiger_error'] = str(e)
        
        return result
    
    def get_company_info(self, stock_code):
        """获取公司基本信息（增强版）"""
        info = {}
        
        try:
            # 判断市场
            if stock_code.startswith('6'):
                market_code = f'1.{stock_code}'
                market = 'sh'
            else:
                market_code = f'0.{stock_code}'
                market = 'sz'
            
            # 东方财富公司信息接口
            url = 'http://push2.eastmoney.com/api/qt/stock/get'
            params = {
                'secid': market_code,
                'fields': 'f57,f58,f84,f85,f86,f127,f116,f117'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('data'):
                d = data['data']
                info['name'] = d.get('f58', '')
                info['high'] = d.get('f84', 0) / 100 if d.get('f84') else 0
                info['low'] = d.get('f85', 0) / 100 if d.get('f85') else 0
                info['volume'] = d.get('f86', 0)
                info['turnover_rate'] = d.get('f127', 0) / 100 if d.get('f127') else 0
            
            # 获取公司详细信息（行业、主营业务等）
            try:
                detail_url = f'http://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/Index'
                detail_params = {
                    'type': 'web',
                    'code': f'{market}{stock_code}'
                }
                detail_response = self.session.get(detail_url, params=detail_params, timeout=10)
                
                # 尝试从HTML中提取信息
                import re
                html = detail_response.text
                
                # 提取行业
                industry_match = re.search(r'所属行业[：:]\s*([^<\n]+)', html)
                if industry_match:
                    info['industry'] = industry_match.group(1).strip()
                else:
                    info['industry'] = '暂无数据'
                
                # 提取主营业务
                business_match = re.search(r'主营业务[：:]\s*([^<\n]{10,200})', html)
                if business_match:
                    info['main_business'] = business_match.group(1).strip()[:100]
                else:
                    info['main_business'] = '暂无数据'
                
                # 提取上市日期
                listing_match = re.search(r'上市时间[：:]\s*(\d{4}-\d{2}-\d{2})', html)
                if listing_match:
                    info['listing_date'] = listing_match.group(1)
                else:
                    info['listing_date'] = '暂无数据'
            
            except Exception as e:
                info['industry'] = '暂无数据'
                info['main_business'] = '暂无数据'
                info['listing_date'] = '暂无数据'
        
        except Exception as e:
            print(f"获取公司信息失败: {e}")
        
        return info
    
    def get_announcements_detailed(self, stock_code, days=30, max_count=5):
        """
        获取详细公告信息（从东方财富股吧公告专区爬取）
        
        Args:
            stock_code: 股票代码
            days: 获取最近多少天的公告，默认30天（1个月）
            max_count: 最多返回多少条公告，默认5条
        
        Returns:
            list: 公告列表
        """
        announcements = []
        
        try:
            from bs4 import BeautifulSoup
            import re
            from datetime import timedelta
            
            # 访问股吧公告专区（参数3代表公告分类）
            url = f'http://guba.eastmoney.com/list,{stock_code},3,f.html'
            
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'  # 使用UTF-8编码
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找公告表格中的所有行
                # 表格结构：阅读数、评论数、标题、公告类型、公告日期
                rows = soup.find_all('tr')
                
                start_date = datetime.now() - timedelta(days=days)
                
                for row in rows:
                    try:
                        # 查找所有单元格
                        cells = row.find_all('td')
                        if len(cells) < 5:
                            continue
                        
                        # 第3列是标题（索引2）
                        title_cell = cells[2]
                        title_link = title_cell.find('a', href=re.compile(r'/news,'))
                        if not title_link:
                            continue
                        
                        title = title_link.get_text(strip=True)
                        href = title_link.get('href', '')
                        
                        # 第4列是公告类型（索引3）
                        ann_type = cells[3].get_text(strip=True)
                        
                        # 第5列是日期（索引4）
                        date_text = cells[4].get_text(strip=True)
                        
                        # 解析日期（格式：01-29 07:05 或 2025-01-29）
                        date_str = ''
                        try:
                            # 提取日期部分（去掉时间）
                            date_part = date_text.split()[0] if ' ' in date_text else date_text
                            
                            if date_part.count('-') == 1:
                                # 短日期格式：01-29
                                current_year = datetime.now().year
                                current_month = datetime.now().month
                                month, day = date_part.split('-')
                                month_int = int(month)
                                
                                # 如果月份大于当前月份，说明是去年的
                                if month_int > current_month:
                                    year = current_year - 1
                                else:
                                    year = current_year
                                
                                date_str = f'{year}-{month.zfill(2)}-{day.zfill(2)}'
                                ann_date = datetime.strptime(date_str, '%Y-%m-%d')
                            elif date_part.count('-') == 2:
                                # 完整日期格式：2025-01-29
                                date_str = date_part
                                ann_date = datetime.strptime(date_str, '%Y-%m-%d')
                            else:
                                continue
                            
                            # 检查是否在时间范围内
                            if ann_date >= start_date:
                                # 智能生成摘要
                                summary = self._generate_announcement_summary(title, ann_type)
                                
                                announcements.append({
                                    'title': title,
                                    'date': date_str,
                                    'type': ann_type if ann_type else '公司公告',
                                    'url': f'http://guba.eastmoney.com{href}' if href.startswith('/') else href,
                                    'summary': summary
                                })
                                
                                # 限制最多max_count条
                                if len(announcements) >= max_count:
                                    break
                        except Exception as date_error:
                            # 日期解析失败，跳过这条
                            continue
                    except Exception as row_error:
                        continue
            
            # 如果没有获取到公告，添加说明
            if not announcements:
                stock_name = self._get_stock_name(stock_code)
                announcements.append({
                    'title': f'{stock_name}({stock_code}) - 近{days}天无公告',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'type': '系统提示',
                    'url': '',
                    'summary': f'该股票在最近{days}天内没有发布公告。这可能是因为：1) 公司处于正常经营状态，无重大事项需披露；2) 非信息披露密集期；3) 建议查看更早期的公告或关注后续更新。'
                })
        
        except Exception as e:
            print(f"获取公告失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 添加说明
            stock_name = self._get_stock_name(stock_code)
            announcements.append({
                'title': f'{stock_name}({stock_code}) - 近{days}天无公告',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'type': '系统提示',
                'url': '',
                'summary': f'该股票在最近{days}天内没有发布公告。这可能是因为：1) 公司处于正常经营状态，无重大事项需披露；2) 非信息披露密集期；3) 建议查看更早期的公告或关注后续更新。'
            })
        
        return announcements
    
    def _get_announcements_backup(self, stock_code, days=7):
        """备用公告获取接口"""
        announcements = []
        
        try:
            # 判断市场
            if stock_code.startswith('6'):
                market = 'sh'
            else:
                market = 'sz'
            
            # 计算起始日期
            from datetime import timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 使用旧版接口
            url = 'http://np-anotice-stock.eastmoney.com/api/security/ann'
            params = {
                'sr': -1,
                'page_size': 50,
                'page_index': 1,
                'ann_type': 'A',
                'client_source': 'web',
                'stock_list': f'{market}{stock_code}',
                'begin_time': start_date.strftime('%Y-%m-%d'),
                'end_time': end_date.strftime('%Y-%m-%d')
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('data') and data['data'].get('list'):
                for item in data['data']['list']:
                    notice_date = item.get('notice_date', '')
                    
                    try:
                        if notice_date:
                            ann_date = datetime.strptime(notice_date.split()[0], '%Y-%m-%d')
                            if ann_date >= start_date:
                                title = item.get('title', '')
                                ann_type = item.get('type_name', '')
                                
                                summary = self._generate_announcement_summary(title, ann_type)
                                
                                ann = {
                                    'title': title,
                                    'date': notice_date,
                                    'type': ann_type,
                                    'url': item.get('adjunct_url', ''),
                                    'summary': summary
                                }
                                
                                announcements.append(ann)
                                
                                if len(announcements) >= 20:
                                    break
                    except:
                        continue
        
        except Exception as e:
            print(f"备用接口获取公告失败: {e}")
        
        return announcements
    
    def _generate_announcement_summary(self, title, ann_type):
        """智能生成公告摘要"""
        # 关键词映射
        keywords_map = {
            '业绩': '公司发布业绩相关公告，涉及财务数据和经营情况',
            '财报': '公司发布财务报告，披露经营业绩和财务状况',
            '年报': '公司发布年度报告，全面披露年度经营情况',
            '季报': '公司发布季度报告，披露季度经营数据',
            '半年报': '公司发布半年度报告，披露上半年经营情况',
            '分红': '公司发布分红派息方案，涉及股东利益分配',
            '派息': '公司发布现金分红方案，向股东派发现金股利',
            '送股': '公司发布送股方案，以资本公积金转增股本',
            '配股': '公司发布配股方案，向现有股东配售新股',
            '重组': '公司发布重大资产重组公告，涉及资产收购或出售',
            '并购': '公司发布并购重组公告，涉及企业合并或收购',
            '增持': '股东增持公司股份，显示对公司信心',
            '减持': '股东减持公司股份，需关注减持原因和规模',
            '回购': '公司回购自身股份，通常用于股权激励或市值管理',
            '股权激励': '公司实施股权激励计划，激励管理层和核心员工',
            '关联交易': '公司与关联方发生交易，需关注交易公允性',
            '诉讼': '公司涉及法律诉讼，可能影响经营和财务',
            '仲裁': '公司涉及仲裁事项，需关注仲裁结果',
            '处罚': '公司或相关人员受到监管处罚，需关注影响',
            '风险': '公司提示经营风险，投资者需谨慎评估',
            '澄清': '公司澄清市场传闻或不实信息',
            '更正': '公司更正此前公告中的错误信息',
            '补充': '公司补充披露相关信息',
            '停牌': '公司股票停牌，通常因重大事项',
            '复牌': '公司股票复牌，重大事项已披露',
            '中标': '公司中标项目，可能增加营业收入',
            '合同': '公司签订重大合同，涉及业务拓展',
            '投资': '公司对外投资，拓展业务或财务投资',
            '募资': '公司募集资金，用于项目建设或补充流动资金',
            '债券': '公司发行债券，进行债务融资',
            '担保': '公司提供担保，需关注担保风险',
            '变更': '公司发生重要事项变更',
            '选举': '公司董事会或监事会换届选举',
            '辞职': '公司高管辞职，需关注原因和影响',
            '任命': '公司任命新的高管人员',
        }
        
        # 根据标题关键词生成摘要
        for keyword, summary in keywords_map.items():
            if keyword in title:
                return summary
        
        # 如果没有匹配到关键词，使用公告类型
        if ann_type:
            return f'{ann_type}类公告，详见公告全文'
        
        # 默认摘要
        return '公司发布公告，详见公告全文'
    
    def get_news_detailed(self, stock_code):
        """获取详细新闻信息（只获取相关新闻）"""
        news = []
        
        try:
            # 先获取股票名称
            stock_name = self._get_stock_name(stock_code)
            
            # 方法1：使用股票代码搜索
            url = 'http://search-api-web.eastmoney.com/search/jsonp'
            params = {
                'cb': 'jQuery',
                'param': json.dumps({
                    'uid': '',
                    'keyword': stock_code,
                    'type': ['cmsArticleWebOld'],
                    'client': 'web',
                    'clientType': 'web',
                    'clientVersion': '1.0',
                    'param': {
                        'cmsArticleWebOld': {
                            'searchScope': 'default',
                            'sort': 'default',
                            'pageIndex': 1,
                            'pageSize': 50  # 获取更多，然后筛选
                        }
                    }
                })
            }
            
            response = self.session.get(url, params=params, timeout=10)
            text = response.text
            
            # 解析JSONP
            try:
                json_str = re.search(r'jQuery\((.*)\)', text).group(1)
                data = json.loads(json_str)
                
                if data.get('result') and data['result'].get('cmsArticleWebOld'):
                    articles = data['result']['cmsArticleWebOld']
                    
                    for article in articles:
                        title = article.get('title', '')
                        content = article.get('content', '')
                        
                        # 清理HTML标签
                        title_clean = re.sub(r'<[^>]+>', '', title)
                        content_clean = re.sub(r'<[^>]+>', '', content)
                        
                        # 清理多余空格和换行
                        title_clean = ' '.join(title_clean.split())
                        content_clean = ' '.join(content_clean.split())
                        
                        # 筛选相关新闻
                        is_relevant = False
                        
                        # 排除龙虎榜相关新闻（因为有专门的龙虎榜数据）
                        if '龙虎榜' in title_clean:
                            continue
                        
                        # 排除通用列表类新闻（优先判断）
                        exclude_patterns = [
                            r'\d+只.*股',  # "73只个股"
                            r'\d+家公司',  # "60家公司"
                            r'今日.*个股',  # "今日48只个股"
                            r'盘中.*个股',  # "盘中突破"
                            r'概念.*涨',   # "小金属概念涨"
                            r'主力资金净流入\d+股',  # "主力资金净流入111股"
                        ]
                        
                        is_excluded = False
                        for pattern in exclude_patterns:
                            if re.search(pattern, title_clean):
                                is_excluded = True
                                break
                        
                        if is_excluded:
                            continue
                        
                        # 1. 标题包含股票代码且不是列表（最相关）
                        if stock_code in title_clean:
                            # 确保不是简单提及，而是主题
                            if len(title_clean) > 10:  # 标题足够长
                                is_relevant = True
                        # 2. 标题包含股票名称（相关）
                        elif stock_name != stock_code and len(stock_name) > 2 and stock_name in title_clean:
                            # 确保不是列表中的一个
                            if len(title_clean) < 50:  # 标题不太长（列表标题通常很长）
                                is_relevant = True
                        
                        if is_relevant:
                            # 生成有意义的摘要
                            if content_clean and len(content_clean) > 20:
                                # 优先提取包含股票代码或名称的句子
                                sentences = re.split(r'[。！？]', content_clean)
                                relevant_sentences = []
                                
                                for sentence in sentences:
                                    if stock_code in sentence or (stock_name != stock_code and stock_name in sentence):
                                        relevant_sentences.append(sentence.strip())
                                        if len('。'.join(relevant_sentences)) > 150:
                                            break
                                
                                if relevant_sentences:
                                    summary = '。'.join(relevant_sentences)[:200]
                                    if not summary.endswith('。'):
                                        summary += '...'
                                else:
                                    # 如果没有相关句子，取开头
                                    summary = content_clean[:200]
                                    if len(content_clean) > 200:
                                        summary += '...'
                            else:
                                summary = f"关于{stock_name}({stock_code})的资讯"
                            
                            news.append({
                                'title': title_clean,
                                'date': article.get('date', ''),
                                'source': article.get('mediaName', '东方财富'),
                                'url': article.get('url', ''),
                                'summary': summary
                            })
                            
                            if len(news) >= 15:
                                break
            except Exception as e:
                print(f"解析新闻数据失败: {e}")
            
            # 如果新闻太少，添加提示
            if len(news) == 0:
                news.append({
                    'title': f'{stock_name}({stock_code}) - 暂无最新专属资讯',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'source': '系统提示',
                    'url': '',
                    'summary': f'当前暂无专门针对{stock_name}({stock_code})的新闻资讯。这可能是因为：1) 该股票近期没有重大新闻；2) 公司处于正常经营状态；3) 建议查看公告信息了解公司动态。'
                })
            elif len(news) < 5:
                # 新闻较少时添加说明
                news.append({
                    'title': f'{stock_name}({stock_code}) - 新闻数量说明',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'source': '系统提示',
                    'url': '',
                    'summary': f'当前仅获取到{len(news)}条与{stock_name}({stock_code})直接相关的新闻。这是正常现象，说明该股票近期新闻报道较少。建议关注公告信息获取更多公司动态。'
                })
        
        except Exception as e:
            print(f"获取新闻失败: {e}")
            # 添加错误提示
            news.append({
                'title': f'{stock_code} - 新闻获取失败',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': '系统提示',
                'url': '',
                'summary': f'获取新闻时出现错误：{str(e)}。请稍后重试或检查网络连接。'
            })
        
        return news
    
    def _get_stock_name(self, stock_code):
        """获取股票名称"""
        try:
            if stock_code.startswith('6'):
                market_code = f'1.{stock_code}'
            else:
                market_code = f'0.{stock_code}'
            
            url = 'http://push2.eastmoney.com/api/qt/stock/get'
            params = {
                'secid': market_code,
                'fields': 'f58'
            }
            
            response = self.session.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get('data'):
                return data['data'].get('f58', stock_code)
        except:
            pass
        
        return stock_code
    
    def get_financial_data_enhanced(self, stock_code):
        """获取增强版财务数据"""
        financial = {}
        
        try:
            # 判断市场
            if stock_code.startswith('6'):
                market_code = f'1.{stock_code}'
            else:
                market_code = f'0.{stock_code}'
            
            # 东方财富财务数据接口
            url = 'http://push2.eastmoney.com/api/qt/stock/get'
            params = {
                'secid': market_code,
                'fields': 'f57,f58,f116,f117,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('data'):
                d = data['data']
                financial['pe_ratio'] = d.get('f162', 0) / 100 if d.get('f162') else 0  # 市盈率
                financial['pb_ratio'] = d.get('f167', 0) / 100 if d.get('f167') else 0  # 市净率
                financial['roe'] = d.get('f164', 0) / 100 if d.get('f164') else 0  # ROE
                financial['total_market_cap'] = d.get('f116', 0) / 100000000 if d.get('f116') else 0  # 总市值（亿）
                financial['circulation_market_cap'] = d.get('f117', 0) / 100000000 if d.get('f117') else 0  # 流通市值（亿）
                financial['eps'] = d.get('f170', 0) / 100 if d.get('f170') else 0  # 每股收益
                financial['bvps'] = d.get('f171', 0) / 100 if d.get('f171') else 0  # 每股净资产
                
                # 计算市销率（如果有数据）
                if d.get('f168'):
                    financial['ps_ratio'] = d.get('f168', 0) / 100
                
                # 计算市现率（如果有数据）
                if d.get('f169'):
                    financial['pcf_ratio'] = d.get('f169', 0) / 100
        
        except Exception as e:
            print(f"获取财务数据失败: {e}")
        
        return financial
    
    def get_research_reports(self, stock_code):
        """获取研报信息"""
        reports = []
        
        try:
            # 判断市场
            if stock_code.startswith('6'):
                market = 'sh'
            else:
                market = 'sz'
            
            # 东方财富研报接口
            url = 'http://reportapi.eastmoney.com/report/list'
            params = {
                'cb': 'datatable',
                'industryCode': '*',
                'pageSize': 10,
                'industry': '*',
                'rating': '*',
                'ratingChange': '*',
                'beginTime': '',
                'endTime': '',
                'pageNo': 1,
                'fields': '',
                'qType': 0,
                'orgCode': '',
                'code': f'{market}{stock_code}',
                '_': '1234567890'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            text = response.text
            
            # 解析JSONP
            try:
                json_str = re.search(r'datatable\((.*)\)', text).group(1)
                data = json.loads(json_str)
                
                if data.get('data'):
                    for item in data['data'][:5]:  # 取前5条
                        reports.append({
                            'title': item.get('title', ''),
                            'org': item.get('orgSName', ''),
                            'researcher': item.get('researcher', ''),
                            'rating': item.get('rating', ''),
                            'date': item.get('publishDate', ''),
                            'summary': item.get('title', '')[:100]
                        })
            except:
                pass
        
        except Exception as e:
            print(f"获取研报失败: {e}")
        
        return reports
    
    def get_capital_flow(self, stock_code):
        """获取资金流向"""
        flow = {}
        
        try:
            # 判断市场
            if stock_code.startswith('6'):
                market_code = f'1.{stock_code}'
            else:
                market_code = f'0.{stock_code}'
            
            # 东方财富资金流向接口
            url = 'http://push2.eastmoney.com/api/qt/stock/fflow/kline/get'
            params = {
                'lmt': 1,
                'klt': 101,
                'secid': market_code,
                'fields1': 'f1,f2,f3,f7',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('data') and data['data'].get('klines'):
                kline = data['data']['klines'][0].split(',')
                if len(kline) >= 7:
                    flow['main_net_inflow'] = float(kline[1]) / 10000  # 主力净流入（万元）
                    flow['small_net_inflow'] = float(kline[2]) / 10000  # 小单净流入（万元）
                    flow['medium_net_inflow'] = float(kline[3]) / 10000  # 中单净流入（万元）
                    flow['large_net_inflow'] = float(kline[4]) / 10000  # 大单净流入（万元）
                    flow['super_net_inflow'] = float(kline[5]) / 10000  # 超大单净流入（万元）
        
        except Exception as e:
            print(f"获取资金流向失败: {e}")
        
        return flow
    
    def get_holder_info(self, stock_code):
        """获取股东信息"""
        holder = {}
        
        try:
            # 判断市场
            if stock_code.startswith('6'):
                market = 'sh'
            else:
                market = 'sz'
            
            # 东方财富股东信息接口
            url = 'http://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/Index'
            params = {
                'type': 'web',
                'code': f'{market}{stock_code}'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            html = response.text
            
            # 提取股东户数
            holder_count_match = re.search(r'股东户数[：:]\s*([0-9,]+)', html)
            if holder_count_match:
                holder['holder_count'] = holder_count_match.group(1)
            
            # 提取人均持股
            avg_hold_match = re.search(r'人均持股[：:]\s*([0-9,.]+)', html)
            if avg_hold_match:
                holder['avg_hold'] = avg_hold_match.group(1)
            
            # 提取前十大股东持股比例
            top10_match = re.search(r'前十大股东持股比例[：:]\s*([0-9.]+)%', html)
            if top10_match:
                holder['top10_ratio'] = float(top10_match.group(1))
        
        except Exception as e:
            print(f"获取股东信息失败: {e}")
        
        return holder
    
    def get_dragon_tiger_list(self, stock_code, days=30):
        """
        获取龙虎榜数据（详细版）
        
        Args:
            stock_code: 股票代码
            days: 获取最近多少天的数据，默认30天
            
        Returns:
            list: 龙虎榜记录列表
        """
        dragon_tiger_list = []
        
        try:
            # 判断市场
            if stock_code.startswith('6'):
                market = 'SH'
            else:
                market = 'SZ'
            
            # 东方财富龙虎榜接口
            url = 'http://datacenter-web.eastmoney.com/api/data/v1/get'
            params = {
                'sortColumns': 'TRADE_DATE,SECURITY_CODE',
                'sortTypes': '-1,-1',
                'pageSize': 50,
                'pageNumber': 1,
                'reportName': 'RPT_DAILYBILLBOARD_DETAILS',
                'columns': 'ALL',
                'filter': f'(SECURITY_CODE="{stock_code}")(TRADE_DATE>=\'{(datetime.now() - __import__("datetime").timedelta(days=days)).strftime("%Y-%m-%d")}\')'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('result') and data['result'].get('data'):
                for item in data['result']['data']:
                    record = {
                        'date': item.get('TRADE_DATE', ''),
                        'reason': item.get('EXPLANATION', ''),  # 上榜原因
                        'close_price': item.get('CLOSE_PRICE', 0),  # 收盘价
                        'change_pct': item.get('CHANGE_RATE', 0),  # 涨跌幅
                        'turnover': item.get('TURNOVER', 0) / 100000000,  # 成交额（亿）
                        'net_amount': item.get('NET_AMT', 0) / 10000,  # 净买入额（万）
                        'buy_amount': item.get('BUY', 0) / 10000,  # 买入额（万）
                        'sell_amount': item.get('SELL', 0) / 10000,  # 卖出额（万）
                        'total_amount': item.get('ACCUM_AMOUNT', 0) / 10000,  # 总成交额（万）
                        'details': []  # 营业部明细
                    }
                    
                    # 获取该日期的营业部明细
                    trade_date = item.get('TRADE_DATE', '')
                    if trade_date:
                        details = self._get_dragon_tiger_details(stock_code, trade_date)
                        record['details'] = details
                    
                    dragon_tiger_list.append(record)
                    
                    # 只保留最近3次
                    if len(dragon_tiger_list) >= 3:
                        break
            
            # 如果没有龙虎榜数据，添加说明
            if not dragon_tiger_list:
                stock_name = self._get_stock_name(stock_code)
                dragon_tiger_list.append({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'reason': f'{stock_name}({stock_code}) - 近1个月未上龙虎榜',
                    'close_price': 0,
                    'change_pct': 0,
                    'turnover': 0,
                    'net_amount': 0,
                    'buy_amount': 0,
                    'sell_amount': 0,
                    'total_amount': 0,
                    'details': [],
                    'note': f'该股票在最近1个月内未登上龙虎榜。龙虎榜通常记录异常波动、涨跌幅较大或成交量异常的股票。未上榜说明该股票交易相对平稳。'
                })
        
        except Exception as e:
            print(f"获取龙虎榜失败: {e}")
            dragon_tiger_list.append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'reason': f'{stock_code} - 龙虎榜数据获取失败',
                'close_price': 0,
                'change_pct': 0,
                'turnover': 0,
                'net_amount': 0,
                'buy_amount': 0,
                'sell_amount': 0,
                'total_amount': 0,
                'details': [],
                'note': f'获取龙虎榜数据时出现错误：{str(e)}。请稍后重试。'
            })
        
        return dragon_tiger_list
    
    def _get_dragon_tiger_details(self, stock_code, trade_date):
        """
        获取龙虎榜营业部明细
        
        Args:
            stock_code: 股票代码
            trade_date: 交易日期
            
        Returns:
            list: 营业部买卖明细
        """
        details = []
        
        try:
            # 东方财富龙虎榜明细接口
            url = 'http://datacenter-web.eastmoney.com/api/data/v1/get'
            params = {
                'sortColumns': 'TRADE_DATE,SECURITY_CODE',
                'sortTypes': '-1,-1',
                'pageSize': 20,
                'pageNumber': 1,
                'reportName': 'RPT_BILLBOARD_DAILYDETAILSBUY',  # 买入明细
                'columns': 'ALL',
                'filter': f'(SECURITY_CODE="{stock_code}")(TRADE_DATE=\'{trade_date}\')'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            # 买入营业部
            buy_list = []
            if data.get('result') and data['result'].get('data'):
                for item in data['result']['data'][:5]:  # 前5大买入
                    buy_list.append({
                        'type': '买入',
                        'name': item.get('OPERATEDEPT_NAME', ''),
                        'buy_amount': item.get('BUY', 0) / 10000,  # 万元
                        'sell_amount': item.get('SELL', 0) / 10000,  # 万元
                        'net_amount': item.get('NET', 0) / 10000  # 净买入（万元）
                    })
            
            # 卖出营业部
            params['reportName'] = 'RPT_BILLBOARD_DAILYDETAILSSELL'
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            sell_list = []
            if data.get('result') and data['result'].get('data'):
                for item in data['result']['data'][:5]:  # 前5大卖出
                    sell_list.append({
                        'type': '卖出',
                        'name': item.get('OPERATEDEPT_NAME', ''),
                        'buy_amount': item.get('BUY', 0) / 10000,  # 万元
                        'sell_amount': item.get('SELL', 0) / 10000,  # 万元
                        'net_amount': item.get('NET', 0) / 10000  # 净卖出（万元）
                    })
            
            details = buy_list + sell_list
        
        except Exception as e:
            print(f"获取龙虎榜明细失败: {e}")
        
        return details
    
    def format_info(self, info):
        """格式化信息为详细文本"""
        text = f"股票代码：{info['code']}\n"
        text += f"获取时间：{info['timestamp']}\n\n"
        
        # 公司信息
        if info.get('company_info'):
            text += "=" * 60 + "\n"
            text += "🏢 公司信息\n"
            text += "=" * 60 + "\n"
            company = info['company_info']
            if company.get('name'):
                text += f"公司名称：{company['name']}\n"
            if company.get('industry'):
                text += f"所属行业：{company['industry']}\n"
            if company.get('main_business'):
                text += f"主营业务：{company['main_business']}\n"
            if company.get('listing_date'):
                text += f"上市日期：{company['listing_date']}\n"
            if company.get('turnover_rate'):
                text += f"换手率：{company['turnover_rate']:.2f}%\n"
            text += "\n"
        
        # 财务数据（增强版）
        if info.get('financial'):
            text += "=" * 60 + "\n"
            text += "💰 财务数据\n"
            text += "=" * 60 + "\n"
            fin = info['financial']
            if fin.get('total_market_cap'):
                text += f"总市值：{fin['total_market_cap']:.2f}亿元\n"
            if fin.get('circulation_market_cap'):
                text += f"流通市值：{fin['circulation_market_cap']:.2f}亿元\n"
            if fin.get('pe_ratio'):
                text += f"市盈率(PE)：{fin['pe_ratio']:.2f}\n"
            if fin.get('pb_ratio'):
                text += f"市净率(PB)：{fin['pb_ratio']:.2f}\n"
            if fin.get('ps_ratio'):
                text += f"市销率(PS)：{fin['ps_ratio']:.2f}\n"
            if fin.get('pcf_ratio'):
                text += f"市现率(PCF)：{fin['pcf_ratio']:.2f}\n"
            if fin.get('roe'):
                text += f"净资产收益率(ROE)：{fin['roe']:.2f}%\n"
            if fin.get('eps'):
                text += f"每股收益(EPS)：{fin['eps']:.2f}元\n"
            if fin.get('bvps'):
                text += f"每股净资产(BVPS)：{fin['bvps']:.2f}元\n"
            text += "\n"
        
        # 资金流向
        if info.get('capital_flow'):
            text += "=" * 60 + "\n"
            text += "💸 资金流向（今日）\n"
            text += "=" * 60 + "\n"
            flow = info['capital_flow']
            if flow.get('main_net_inflow') is not None:
                text += f"主力净流入：{flow['main_net_inflow']:.2f}万元\n"
            if flow.get('super_net_inflow') is not None:
                text += f"超大单净流入：{flow['super_net_inflow']:.2f}万元\n"
            if flow.get('large_net_inflow') is not None:
                text += f"大单净流入：{flow['large_net_inflow']:.2f}万元\n"
            if flow.get('medium_net_inflow') is not None:
                text += f"中单净流入：{flow['medium_net_inflow']:.2f}万元\n"
            if flow.get('small_net_inflow') is not None:
                text += f"小单净流入：{flow['small_net_inflow']:.2f}万元\n"
            text += "\n"
        
        # 股东信息
        if info.get('holder_info'):
            text += "=" * 60 + "\n"
            text += "👥 股东信息\n"
            text += "=" * 60 + "\n"
            holder = info['holder_info']
            if holder.get('holder_count'):
                text += f"股东户数：{holder['holder_count']}\n"
            if holder.get('avg_hold'):
                text += f"人均持股：{holder['avg_hold']}股\n"
            if holder.get('top10_ratio'):
                text += f"前十大股东持股比例：{holder['top10_ratio']:.2f}%\n"
            text += "\n"
        
        # 研报
        if info.get('research_reports'):
            text += "=" * 60 + "\n"
            text += "📊 研究报告\n"
            text += "=" * 60 + "\n"
            if info['research_reports']:
                for i, report in enumerate(info['research_reports'], 1):
                    text += f"\n{i}. {report['title']}\n"
                    text += f"   机构：{report['org']}\n"
                    text += f"   研究员：{report['researcher']}\n"
                    text += f"   评级：{report['rating']}\n"
                    text += f"   日期：{report['date']}\n"
            else:
                text += "暂无研报信息\n"
            text += "\n"
        
        # 公告
        text += "=" * 60 + "\n"
        text += "📢 公告信息（近1个月，最近5条）\n"
        text += "=" * 60 + "\n"
        if info['announcements']:
            # 统计公告数量
            real_announcements = [ann for ann in info['announcements'] if ann.get('type') != '系统提示']
            if real_announcements:
                text += f"共获取到 {len(real_announcements)} 条公告\n\n"
                for i, ann in enumerate(real_announcements[:5], 1):  # 只显示前5条
                    text += f"{i}. {ann['title']}\n"
                    text += f"   日期：{ann['date']}\n"
                    text += f"   类型：{ann['type']}\n"
                    text += f"   摘要：{ann['summary']}\n\n"
                
                if len(real_announcements) > 5:
                    text += f"...还有 {len(real_announcements) - 5} 条公告未显示\n"
            else:
                # 显示系统提示
                for ann in info['announcements']:
                    text += f"{ann['summary']}\n"
        else:
            text += "暂无公告信息\n"
        
        # 新闻
        text += "\n" + "=" * 60 + "\n"
        text += "📰 新闻资讯\n"
        text += "=" * 60 + "\n"
        if info['news']:
            for i, news in enumerate(info['news'][:10], 1):  # 显示前10条
                text += f"\n{i}. {news['title']}\n"
                text += f"   日期：{news['date']}\n"
                text += f"   来源：{news['source']}\n"
                if news.get('summary'):
                    text += f"   摘要：{news['summary']}\n"
        else:
            text += "暂无新闻资讯\n"
        
        # 龙虎榜
        if info.get('dragon_tiger'):
            text += "\n" + "=" * 60 + "\n"
            text += "🐉 龙虎榜数据（近1个月，最近3次）\n"
            text += "=" * 60 + "\n"
            
            dragon_tiger = info['dragon_tiger']
            real_records = [rec for rec in dragon_tiger if not rec.get('note')]
            
            if real_records:
                text += f"共上榜 {len(real_records)} 次\n\n"
                
                for i, record in enumerate(real_records, 1):
                    text += f"┌─ 第{i}次上榜 ─────────────────────────────────────┐\n"
                    text += f"│ 日期：{record['date']}\n"
                    text += f"│ 上榜原因：{record['reason']}\n"
                    text += f"│ 收盘价：{record['close_price']:.2f}元\n"
                    text += f"│ 涨跌幅：{record['change_pct']:+.2f}%\n"
                    text += f"│ 成交额：{record['turnover']:.2f}亿元\n"
                    text += f"│ 龙虎榜净买入：{record['net_amount']:+.2f}万元\n"
                    text += f"│ 龙虎榜买入额：{record['buy_amount']:.2f}万元\n"
                    text += f"│ 龙虎榜卖出额：{record['sell_amount']:.2f}万元\n"
                    text += f"└────────────────────────────────────────────────┘\n"
                    
                    # 营业部明细
                    if record.get('details'):
                        # 买入营业部
                        buy_details = [d for d in record['details'] if d['type'] == '买入']
                        if buy_details:
                            text += "\n  ┌─ 买入前5大营业部 ─────────────────────────────┐\n"
                            for j, detail in enumerate(buy_details, 1):
                                text += f"  │ {j}. {detail['name']}\n"
                                text += f"  │    买入：{detail['buy_amount']:>10.2f}万元\n"
                                text += f"  │    卖出：{detail['sell_amount']:>10.2f}万元\n"
                                text += f"  │    净额：{detail['net_amount']:>+10.2f}万元\n"
                                if j < len(buy_details):
                                    text += f"  │    ────────────────────────────────────────\n"
                            text += f"  └────────────────────────────────────────────────┘\n"
                        
                        # 卖出营业部
                        sell_details = [d for d in record['details'] if d['type'] == '卖出']
                        if sell_details:
                            text += "\n  ┌─ 卖出前5大营业部 ─────────────────────────────┐\n"
                            for j, detail in enumerate(sell_details, 1):
                                text += f"  │ {j}. {detail['name']}\n"
                                text += f"  │    买入：{detail['buy_amount']:>10.2f}万元\n"
                                text += f"  │    卖出：{detail['sell_amount']:>10.2f}万元\n"
                                text += f"  │    净额：{detail['net_amount']:>+10.2f}万元\n"
                                if j < len(sell_details):
                                    text += f"  │    ────────────────────────────────────────\n"
                            text += f"  └────────────────────────────────────────────────┘\n"
                    
                    text += "\n"
            else:
                # 显示未上榜说明
                for record in dragon_tiger:
                    if record.get('note'):
                        text += f"{record['note']}\n"
        
        return text


if __name__ == '__main__':
    # 测试
    crawler = StockInfoCrawler()
    
    print("测试获取股票详细信息...")
    info = crawler.get_stock_info('600519')
    
    print(crawler.format_info(info))
