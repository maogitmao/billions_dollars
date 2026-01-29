#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Billions Dollars - 交易控制面板主界面

⚠️ 项目规则：
- 代码即文档，不创建冗余说明文档
- 安装说明存放：docs/INSTALL.md
- 测试文件存放：tests/
- 所有说明都在代码注释中

功能说明：
1. 实时行情监控 - 1秒刷新，支持200+股票
2. 分时图显示 - 3秒刷新，显示当日走势
3. K线图+MACD - 10秒刷新，技术分析
4. AI对话助手 - 智能分析，自然语言交互（异步调用，不阻塞UI）
   - 自动使用程序中的实时行情数据
   - 询问股票代码（如：002342）会提供该股票的实时数据
   - 询问"行情列表"会分析列表中的所有股票
   - 选中股票后提问，会自动使用该股票的数据
5. 输入法支持 - 自动检测fcitx5/fcitx/ibus

启动方式：
- bash start_with_ime.sh  # 推荐，自动检测输入法
- python3 main.py         # 自动检测运行中的输入法进程

输入法问题：
如果无法输入中文：
1. 确保fcitx5正在运行：ps aux | grep fcitx5
2. 安装系统PyQt5（pip版本不包含fcitx5插件）：
   pip uninstall PyQt5 PyQt5-sip
   sudo apt install python3-pyqt5 python3-pyqt5.qtchart
3. 使用启动脚本：bash start_with_ime.sh
4. 在输入框中按 Ctrl+Space 切换输入法
5. 运行诊断：bash check_ime.sh

注意：
- pip安装的PyQt5只包含ibus插件，不包含fcitx5插件
- 系统apt安装的python3-pyqt5包含完整的输入法插件支持
- AI输入框使用QTextEdit，对输入法支持更好
"""

import sys
import json
import os

# 设置输入法支持（必须在导入PyQt5之前）
if os.name == 'posix':  # Linux/Unix
    # 支持fcitx5、fcitx、ibus等输入法
    # 强制覆盖系统默认设置，优先使用fcitx5
    import subprocess
    
    try:
        # 检查fcitx5进程
        subprocess.run(['pgrep', '-x', 'fcitx5'], check=True, capture_output=True)
        os.environ['QT_IM_MODULE'] = 'fcitx5'  # 强制使用fcitx5
        os.environ['GTK_IM_MODULE'] = 'fcitx5'
        os.environ['XMODIFIERS'] = '@im=fcitx5'
    except:
        try:
            # 检查fcitx进程
            subprocess.run(['pgrep', '-x', 'fcitx'], check=True, capture_output=True)
            if 'QT_IM_MODULE' not in os.environ:
                os.environ['QT_IM_MODULE'] = 'fcitx'
        except:
            # 默认使用fcitx5（最常见）
            if 'QT_IM_MODULE' not in os.environ:
                os.environ['QT_IM_MODULE'] = 'fcitx5'

from datetime import datetime

# 抑制pandas的pyarrow警告
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pandas')

import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QSplitter, QTextEdit, QLabel, 
    QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor
from data.fetchers.realtime_fetcher import RealtimeFetcher
from core.quote_manager import QuoteManager
from config import THREAD_POOL_CONFIG

# 配置matplotlib中文字体
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'Noto Sans CJK TC', 'DejaVu Sans', 'SimHei', 'Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class AIWorkerThread(QThread):
    """AI工作线程 - 避免阻塞UI"""
    finished = pyqtSignal(str)  # 完成信号，返回AI回复
    
    def __init__(self, llm_client, message, system_prompt, context):
        super().__init__()
        self.llm_client = llm_client
        self.message = message
        self.system_prompt = system_prompt
        self.context = context
    
    def run(self):
        """在后台线程中调用AI"""
        try:
            # 构建完整消息
            full_message = f"{self.context}\n用户问题：{self.message}"
            
            # 调用大模型
            response = self.llm_client.chat(
                full_message,
                system_prompt=self.system_prompt
            )
            
            self.finished.emit(response)
        except Exception as e:
            self.finished.emit(f"AI服务错误: {str(e)}")


class TradingPanel(QMainWindow):
    """交易控制面板主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 启用输入法支持
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
        
        self.stock_list = []  # 存储添加的股票代码
        self.quote_cache = {}  # 缓存行情数据
        self.kline_cache = {}  # 缓存K线数据
        self.timeshare_cache = {}  # 缓存分时数据
        
        # 初始化AI客户端
        try:
            from ai.llm_client import LLMClient, STOCK_ANALYSIS_PROMPT
            self.llm_client = LLMClient()
            self.stock_analysis_prompt = STOCK_ANALYSIS_PROMPT
            self.use_real_ai = True
            # 检查服务状态
            status, msg = self.llm_client.check_status()
            if not status:
                self.use_real_ai = False
                print(f"⚠️ AI服务未就绪: {msg}")
        except Exception as e:
            self.use_real_ai = False
            print(f"⚠️ AI模块加载失败: {e}")
        
        # 使用新的行情管理器（线程池，支持200+股票）
        max_workers = THREAD_POOL_CONFIG.get('max_workers', 30)
        self.quote_manager = QuoteManager(max_workers=max_workers)
        self.quote_manager.quote_updated.connect(self.on_quote_ready)
        self.quote_manager.batch_progress.connect(self.on_batch_progress)
        self.quote_manager.all_completed.connect(self.on_all_quotes_completed)
        
        # 使用脚本所在目录作为基准路径
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.stock_file = os.path.join(self.base_dir, 'stock_list.json')
        
        # K线加载防抖动定时器
        self.kline_load_timer = QTimer()
        self.kline_load_timer.setSingleShot(True)
        self.kline_load_timer.timeout.connect(self._do_load_kline)
        self.pending_stock_code = None
        
        # 分时图加载防抖动定时器
        self.timeshare_load_timer = QTimer()
        self.timeshare_load_timer.setSingleShot(True)
        self.timeshare_load_timer.timeout.connect(self._do_load_timeshare)
        self.pending_timeshare_code = None
        
        # 刷新进度统计
        self.refresh_start_time = None
        
        self.init_ui()
        self.load_stock_list()  # 加载保存的股票列表（会自动确保000001在第一位）
        
        self.update_display()
        self.setup_timer()  # 设置定时刷新
        self.refresh_quotes()  # 立即刷新一次行情
        
        # 延迟选中第一只股票，确保界面完全初始化后再加载图表
        QTimer.singleShot(1000, self._select_first_stock)
    
    def load_stock_list(self):
        """从文件加载股票列表"""
        if os.path.exists(self.stock_file):
            try:
                with open(self.stock_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stock_list = data.get('stocks', [])
                    
                if self.stock_list:
                    print(f"📂 已加载 {len(self.stock_list)} 只股票: {self.stock_list}")
                    self.log_message(f"📂 已加载 {len(self.stock_list)} 只股票")
                else:
                    print("📂 股票列表为空")
            except Exception as e:
                print(f"⚠️ 加载股票列表失败: {str(e)}")
                self.log_message(f"⚠️ 加载股票列表失败: {str(e)}")
        else:
            print(f"📂 股票列表文件不存在: {self.stock_file}")
        
        # 确保999999上证指数始终在第一个位置
        if '999999' in self.stock_list:
            self.stock_list.remove('999999')
        self.stock_list.insert(0, '999999')
        self.log_message("📊 上证指数(999999)已设为默认首位")
    
    def save_stock_list(self):
        """保存股票列表到文件"""
        try:
            data = {
                'stocks': self.stock_list,
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(self.stock_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.log_message(f"💾 已保存 {len(self.stock_list)} 只股票")
        except Exception as e:
            self.log_message(f"❌ 保存股票列表失败: {str(e)}")
    
    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        # 保存股票列表
        self.save_stock_list()
        
        # 停止定时器
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'kline_refresh_timer'):
            self.kline_refresh_timer.stop()
        
        # 等待线程池完成
        if hasattr(self, 'quote_manager'):
            self.quote_manager.wait_for_done(3000)
        
        event.accept()
    
    def setup_timer(self):
        """设置定时器，快速刷新行情"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_quotes)
        self.timer.start(1000)  # 1秒刷新一次行情，更快的实时性
        
        # K线图刷新定时器（每10秒刷新一次当前显示的K线图）
        self.kline_refresh_timer = QTimer()
        self.kline_refresh_timer.timeout.connect(self.refresh_current_kline)
        self.kline_refresh_timer.start(10000)  # 10秒刷新一次K线
        
        # 分时图刷新定时器（每3秒刷新一次）
        self.timeshare_refresh_timer = QTimer()
        self.timeshare_refresh_timer.timeout.connect(self.refresh_current_timeshare)
        self.timeshare_refresh_timer.start(3000)  # 3秒刷新一次分时图
        
        # 启动后预加载前几只股票的数据（提升首次切换速度）
        # 暂时禁用自动预加载，避免启动时跳动
        # QTimer.singleShot(1000, self._preload_initial_stocks)
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Billions Dollars - 交易控制面板")
        # 窗口尺寸：宽度2760，高度1932（在2400x1680基础上增加15%）
        self.setGeometry(0, 0, 2760, 1932)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建分割器（上下分割）
        main_splitter = QSplitter(Qt.Vertical)
        
        # 上半部分（左中右分割）
        top_splitter = QSplitter(Qt.Horizontal)
        
        # 1. 行情显示区域
        market_widget = self.create_market_widget()
        top_splitter.addWidget(market_widget)
        
        # 2. 中间区域（分时图和AI区域）
        middle_widget = self.create_middle_widget()
        top_splitter.addWidget(middle_widget)
        
        # 3. K线图显示区域
        chart_widget = self.create_chart_widget()
        top_splitter.addWidget(chart_widget)
        
        # 调整上半部分左中右比例 - 行情区域占3份，中间区域占2份，K线区域占2份
        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 2)
        top_splitter.setStretchFactor(2, 2)
        
        main_splitter.addWidget(top_splitter)
        
        # 中间功能按键区域
        function_widget = self.create_function_widget()
        main_splitter.addWidget(function_widget)
        
        # 下半部分（左右分割）
        bottom_splitter = QSplitter(Qt.Horizontal)
        
        # 3. 日志输出区域
        log_widget = self.create_log_widget()
        bottom_splitter.addWidget(log_widget)
        
        # 4. 交易界面区域
        trade_widget = self.create_trade_widget()
        bottom_splitter.addWidget(trade_widget)
        
        # 设置下半部分比例
        bottom_splitter.setStretchFactor(0, 1)
        bottom_splitter.setStretchFactor(1, 1)
        
        main_splitter.addWidget(bottom_splitter)
        
        # 调整上中下比例 - 上半部分占3份，功能区占0.5份，下半部分占2份
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 0)  # 功能区固定高度
        main_splitter.setStretchFactor(2, 2)
        
        main_layout.addWidget(main_splitter)
    
    def create_function_widget(self):
        """创建功能按键区域"""
        widget = QWidget()
        widget.setMaximumHeight(80)  # 固定高度
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 标题
        label = QLabel("⚡ 功能区")
        label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(label)
        
        # 弹簧，将按钮推到左边
        layout.addStretch()
        
        # 设置背景色
        widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
            }
        """)
        
        return widget
    
    def fetch_stock_info(self):
        """获取股票信息"""
        # 获取当前选中的股票
        current_row = self.stock_table.currentRow()
        if current_row < 0 or current_row >= len(self.stock_list):
            self.fetch_status_label.setText("⚠️ 请先选择一只股票")
            self.log_message("⚠️ 请先选择一只股票")
            return
        
        stock_code = self.stock_list[current_row]
        stock_name = self.quote_cache.get(stock_code, {}).get('name', stock_code)
        
        # 禁用按钮，显示加载状态
        self.fetch_info_btn.setEnabled(False)
        self.fetch_status_label.setText(f"正在获取 {stock_name}({stock_code}) 的信息...")
        self.log_message(f"📥 开始获取 {stock_name}({stock_code}) 的信息...")
        
        # 在后台线程中获取信息
        class FetchInfoThread(QThread):
            finished = pyqtSignal(dict)
            
            def __init__(self, stock_code):
                super().__init__()
                self.stock_code = stock_code
            
            def run(self):
                from data.fetchers.stock_info_crawler import StockInfoCrawler
                crawler = StockInfoCrawler()
                info = crawler.get_stock_info(self.stock_code)
                self.finished.emit(info)
        
        # 创建并启动线程
        self.fetch_thread = FetchInfoThread(stock_code)
        self.fetch_thread.finished.connect(lambda info: self.on_stock_info_fetched(info, stock_name))
        self.fetch_thread.start()
    
    def on_stock_info_fetched(self, info, stock_name):
        """股票信息获取完成"""
        # 恢复按钮
        self.fetch_info_btn.setEnabled(True)
        
        # 统计信息
        ann_count = len(info.get('announcements', []))
        news_count = len(info.get('news', []))
        research_count = len(info.get('research_reports', []))
        dragon_tiger_count = len([r for r in info.get('dragon_tiger', []) if not r.get('note')])
        
        status_text = f"✅ 获取成功："
        if ann_count > 0:
            status_text += f"{ann_count}条公告"
        if news_count > 0:
            status_text += f"，{news_count}条新闻"
        if research_count > 0:
            status_text += f"，{research_count}条研报"
        if dragon_tiger_count > 0:
            status_text += f"，{dragon_tiger_count}次龙虎榜"
        if info.get('capital_flow'):
            status_text += "，资金流向"
        if info.get('holder_info'):
            status_text += "，股东信息"
        
        self.fetch_status_label.setText(status_text)
        
        log_msg = f"✅ {stock_name}({info['code']}) 信息获取成功："
        if ann_count > 0:
            log_msg += f" {ann_count}条公告"
        if news_count > 0:
            log_msg += f" {news_count}条新闻"
        if research_count > 0:
            log_msg += f" {research_count}条研报"
        if dragon_tiger_count > 0:
            log_msg += f" {dragon_tiger_count}次龙虎榜"
        self.log_message(log_msg)
        
        # 格式化信息
        from data.fetchers.stock_info_crawler import StockInfoCrawler
        crawler = StockInfoCrawler()
        formatted_text = crawler.format_info(info)
        
        # 在AI对话框中显示详细信息
        self.add_ai_message("system", formatted_text)
        
        # 同时发送给AI（如果AI可用）
        if hasattr(self, 'use_real_ai') and self.use_real_ai:
            # 自动向AI发送信息
            ai_message = f"我刚获取了{stock_name}({info['code']})的最新详细信息，包括"
            details = []
            if ann_count > 0:
                details.append(f"{ann_count}条公告")
            if news_count > 0:
                details.append(f"{news_count}条新闻")
            if research_count > 0:
                details.append(f"{research_count}条研报")
            if dragon_tiger_count > 0:
                details.append(f"{dragon_tiger_count}次龙虎榜记录")
            if info.get('capital_flow'):
                details.append("资金流向")
            if info.get('holder_info'):
                details.append("股东信息")
            
            ai_message += "、".join(details) + "。请帮我分析一下这些信息的重点。"
            
            # 构建详细上下文
            context = f"【股票详细信息】\n{formatted_text}\n\n"
            
            # 添加到AI对话
            self.add_ai_message("user", ai_message)
            self.add_ai_message("ai", "正在分析...")
            
            # 异步调用AI
            self._generate_real_ai_response_with_context(ai_message, context)
    
    def _generate_real_ai_response_with_context(self, message, context):
        """使用自定义上下文生成AI回复"""
        try:
            # 创建工作线程
            self.ai_worker = AIWorkerThread(
                self.llm_client,
                message,
                self.stock_analysis_prompt,
                context
            )
            
            # 连接完成信号
            self.ai_worker.finished.connect(self._on_ai_response_ready)
            
            # 启动线程
            self.ai_worker.start()
            
        except Exception as e:
            # 移除"正在分析"
            if self.ai_messages:
                self.ai_messages.pop()
            error_msg = f"AI服务错误: {str(e)}"
            self.add_ai_message("ai", error_msg)
    
    def create_market_widget(self):
        """创建行情显示区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 标题
        label = QLabel("📈 实时行情")
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        label.setFixedHeight(40)
        layout.addWidget(label)
        
        # 添加股票输入区域
        input_layout = QHBoxLayout()
        
        self.stock_input = QLineEdit()
        self.stock_input.setPlaceholderText("输入股票代码（如：600000、000001、600519）")
        self.stock_input.returnPressed.connect(self.add_stock)
        # 强制启用输入法支持
        self.stock_input.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.stock_input.setInputMethodHints(Qt.ImhPreferLatin)
        self.stock_input.setFocusPolicy(Qt.StrongFocus)
        self.stock_input.setFixedHeight(35)
        input_layout.addWidget(self.stock_input)
        
        add_button = QPushButton("添加股票")
        add_button.clicked.connect(self.add_stock)
        add_button.setStyleSheet("padding: 5px 15px; font-weight: bold;")
        add_button.setFixedHeight(35)
        input_layout.addWidget(add_button)
        
        # 删除按钮
        delete_button = QPushButton("删除选中")
        delete_button.clicked.connect(self.delete_selected_stock)
        delete_button.setStyleSheet("padding: 5px 15px; font-weight: bold;")
        delete_button.setFixedHeight(35)
        input_layout.addWidget(delete_button)
        
        # 手动刷新按钮
        refresh_button = QPushButton("🔄 刷新")
        refresh_button.clicked.connect(self.manual_refresh)
        refresh_button.setStyleSheet("padding: 5px 15px; font-weight: bold;")
        refresh_button.setFixedHeight(35)
        input_layout.addWidget(refresh_button)
        
        # 线程池状态标签
        self.thread_status_label = QLabel("线程: 0/30")
        self.thread_status_label.setStyleSheet("font-size: 12px; padding: 5px;")
        self.thread_status_label.setFixedHeight(35)
        input_layout.addWidget(self.thread_status_label)
        
        layout.addLayout(input_layout)
        
        # 创建表格显示行情
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(8)
        self.stock_table.setHorizontalHeaderLabels([
            '代码', '名称', '涨幅%', '现价', '涨跌', '总市值', '流通值', '振幅%'
        ])
        
        # 设置表格样式
        self.stock_table.setAlternatingRowColors(True)
        self.stock_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        
        # 设置列宽自适应
        header = self.stock_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # 设置选择模式为整行选择
        self.stock_table.setSelectionBehavior(QTableWidget.SelectRows)
        # 设置单选模式
        self.stock_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # 连接点击事件
        self.stock_table.cellClicked.connect(self.on_stock_selected)
        # 连接当前行变化事件（支持键盘导航）
        self.stock_table.currentCellChanged.connect(self.on_current_cell_changed)
        
        layout.addWidget(self.stock_table)
        
        return widget
    
    def on_current_cell_changed(self, current_row, current_col, previous_row, previous_col):
        """当前单元格变化时触发（包括键盘导航）- 完全独立的防抖动机制"""
        if current_row >= 0 and current_row < len(self.stock_list):
            stock_code = self.stock_list[current_row]
            
            # 立即更新pending状态，但不加载图表
            # 这样列表选择完全不受图表加载影响
            self.pending_stock_code = stock_code
            self.pending_timeshare_code = stock_code
            
            # 停止所有正在进行的加载
            self.kline_load_timer.stop()
            self.timeshare_load_timer.stop()
            
            # 只有当用户停止移动300ms后，才开始加载图表
            # 这样快速移动时完全不会触发加载，保证列表选择流畅
            self.kline_load_timer.start(300)
            self.timeshare_load_timer.start(300)
    
    def _preload_adjacent_stocks(self, current_row):
        """预加载相邻股票的数据（后台异步加载）"""
        # 预加载上下各1只股票
        adjacent_rows = []
        if current_row > 0:
            adjacent_rows.append(current_row - 1)
        if current_row < len(self.stock_list) - 1:
            adjacent_rows.append(current_row + 1)
        
        for row in adjacent_rows:
            stock_code = self.stock_list[row]
            # 如果缓存中没有，后台加载
            if stock_code not in self.kline_cache:
                # 使用QTimer延迟加载，避免阻塞当前股票的显示
                QTimer.singleShot(200, lambda code=stock_code: self.load_kline_chart(code, silent=True))
            if stock_code not in self.timeshare_cache:
                QTimer.singleShot(200, lambda code=stock_code: self.load_timeshare_chart(code, silent=True))
    
    def _preload_initial_stocks(self):
        """预加载前几只股票的数据（启动时后台加载）"""
        # 预加载前3只股票
        preload_count = min(3, len(self.stock_list))
        for i in range(preload_count):
            stock_code = self.stock_list[i]
            # 延迟加载，避免启动时卡顿
            delay = i * 500  # 每只股票间隔500ms
            QTimer.singleShot(delay, lambda code=stock_code: self.load_kline_chart(code, silent=True))
            QTimer.singleShot(delay + 100, lambda code=stock_code: self.load_timeshare_chart(code, silent=True))
    
    def _select_first_stock(self):
        """选中第一只股票（延迟执行，确保界面完全初始化）"""
        if len(self.stock_list) > 0:
            # 清空缓存，确保重新加载包含volume的数据
            self.kline_cache.clear()
            self.timeshare_cache.clear()
            
            # 选中第一只股票
            self.stock_table.setCurrentCell(0, 0)
            self.log_message(f"📊 已选中第一只股票：{self.stock_list[0]}")
    
    def delete_selected_stock(self):
        """删除选中的股票"""
        selected_rows = self.stock_table.selectedIndexes()
        if not selected_rows:
            self.log_message("⚠️ 请先选择要删除的股票")
            return
        
        # 获取选中的行号（去重）
        rows = sorted(set(index.row() for index in selected_rows), reverse=True)
        
        for row in rows:
            if row < len(self.stock_list):
                stock_code = self.stock_list[row]
                
                # 不允许删除999999上证指数
                if stock_code == '999999':
                    self.log_message("⚠️ 上证指数(999999)是系统默认股票，不能删除")
                    continue
                
                self.stock_list.pop(row)
                self.log_message(f"🗑️ 已删除股票：{stock_code}")
        
        # 保存到文件
        self.save_stock_list()
        
        # 更新显示
        self.update_display()
    
    def manual_refresh(self):
        """手动刷新行情"""
        active_threads = self.quote_manager.get_active_count()
        self.log_message(f"🔄 手动刷新 {len(self.stock_list)} 只股票 (并发: {active_threads})")
        self.refresh_quotes()
    
    def on_stock_selected(self, row, column):
        """股票被点击时 - 已由on_current_cell_changed处理，此方法可删除但保留以防兼容性问题"""
        pass
    
    def _do_load_kline(self):
        """实际执行K线加载（防抖动后）- 用户停止移动后才执行"""
        if self.pending_stock_code:
            stock_code = self.pending_stock_code
            
            # 如果有缓存，立即显示
            if stock_code in self.kline_cache:
                self._render_kline_from_cache(stock_code)
            else:
                # 无缓存，加载数据
                self.load_kline_chart(stock_code)
    
    def _do_load_timeshare(self):
        """实际执行分时图加载（防抖动后）- 用户停止移动后才执行"""
        if self.pending_timeshare_code:
            stock_code = self.pending_timeshare_code
            
            # 如果有缓存，立即显示
            if stock_code in self.timeshare_cache:
                self._render_timeshare_from_cache(stock_code)
            else:
                # 无缓存，加载数据
                self.load_timeshare_chart(stock_code, silent=True)
    
    def _render_kline_from_cache(self, stock_code):
        """从缓存渲染K线图（快速显示）"""
        if stock_code not in self.kline_cache:
            return
        
        # 检查是否还是当前选中的股票（避免渲染过时的数据）
        if stock_code != self.pending_stock_code:
            return
        
        df = self.kline_cache[stock_code]
        stock_name = self.quote_cache.get(stock_code, {}).get('name', stock_code)
        
        # 清空之前的图表（快速清空）
        self.ax.cla()  # K线图
        self.ax_volume.cla()  # 成交量
        self.ax_macd.cla()  # MACD
        
        # 绘制K线图、成交量和MACD
        self.plot_kline_with_ma(df, stock_code, stock_name)
        
        # 异步绘制，不阻塞
        self.canvas.draw_idle()
    
    def _render_timeshare_from_cache(self, stock_code):
        """从缓存渲染分时图（快速显示）"""
        if stock_code not in self.timeshare_cache:
            return
        
        # 检查是否还是当前选中的股票（避免渲染过时的数据）
        if stock_code != self.pending_timeshare_code:
            return
        
        df = self.timeshare_cache[stock_code]
        stock_name = self.quote_cache.get(stock_code, {}).get('name', stock_code)
        
        # 清空之前的图表（快速清空）
        self.timeshare_ax.cla()  # cla()比clear()更快
        
        # 绘制分时图
        self.plot_timeshare(df, stock_code, stock_name)
        
        # 异步绘制，不阻塞
        self.timeshare_canvas.draw_idle()
    
    def load_timeshare_chart(self, stock_code, silent=False, fast_update=False):
        """加载分时图（优化版）
        
        Args:
            stock_code: 股票代码
            silent: 是否静默模式（不输出日志）
            fast_update: 是否快速更新模式（仅更新数据，不重建整个图表）
        """
        from data.fetchers.timeshare_fetcher import TimeshareFetcher
        
        # 检查缓存
        if stock_code in self.timeshare_cache and not fast_update:
            self._render_timeshare_from_cache(stock_code)
            return
        
        if not silent:
            self.log_message(f"📈 正在加载 {stock_code} 的分时图...")
        
        try:
            # 获取分时数据
            fetcher = TimeshareFetcher()
            df = fetcher.get_timeshare_data(stock_code)
            
            if df is None or df.empty:
                if not silent:
                    self.log_message(f"❌ 无法获取 {stock_code} 的分时数据")
                return
            
            # 缓存分时数据
            self.timeshare_cache[stock_code] = df
            
            # 清空之前的图表
            self.timeshare_ax.clear()
            
            # 绘制分时图
            stock_name = self.quote_cache.get(stock_code, {}).get('name', stock_code)
            self.plot_timeshare(df, stock_code, stock_name)
            
            # 使用异步绘制，避免卡顿
            self.timeshare_canvas.draw_idle()
            
            if not silent:
                self.log_message(f"✅ {stock_code} 分时图加载成功")
            
        except Exception as e:
            if not silent:
                self.log_message(f"❌ 加载分时图失败: {str(e)}")
            print(f"分时图错误: {e}")
            import traceback
            traceback.print_exc()
    
    def plot_timeshare(self, df, stock_code, stock_name):
        """绘制分时图（优化版：更平滑、更细腻）"""
        import numpy as np
        from scipy.interpolate import make_interp_spline
        
        # 设置标题
        self.timeshare_ax.set_title(f'{stock_code} - Timeshare Chart', fontsize=12, pad=8)
        
        # 准备数据
        times = df['time'].values
        prices = df['price'].values
        avg_prices = df['avg_price'].values
        pre_close = df['pre_close'].iloc[0]
        
        # 获取当前价格和涨跌幅（优先从quote_cache获取，确保与行情列表一致）
        current_price = prices[-1]
        change_pct = (current_price - pre_close) / pre_close * 100 if pre_close > 0 else 0
        
        if stock_code in self.quote_cache:
            quote = self.quote_cache[stock_code]
            realtime_price = quote.get('price', 0)
            if realtime_price > 0:
                current_price = realtime_price
            # 使用quote_cache中的涨跌幅，确保与行情列表一致
            change_pct = quote.get('change_pct', change_pct)
        
        # 生成完整的时间轴（全天4小时，240分钟）
        full_time_labels = []
        full_time_indices = []
        idx = 0
        
        # 上午 9:30-11:30 (120分钟)
        for hour in [9, 10, 11]:
            start_min = 30 if hour == 9 else 0
            end_min = 30 if hour == 11 else 60
            for minute in range(start_min, end_min):
                full_time_labels.append(f"{hour:02d}:{minute:02d}")
                full_time_indices.append(idx)
                idx += 1
        
        # 下午 13:00-15:00 (120分钟)
        for hour in [13, 14]:
            for minute in range(0, 60):
                full_time_labels.append(f"{hour:02d}:{minute:02d}")
                full_time_indices.append(idx)
                idx += 1
        
        total_minutes = 240  # 全天总分钟数
        
        # 将实际数据映射到完整时间轴
        x_data = []
        valid_prices = []
        valid_avg_prices = []
        
        for i, t in enumerate(times):
            # 找到时间在完整时间轴中的位置
            try:
                pos = full_time_labels.index(t)
                x_data.append(pos)
                valid_prices.append(prices[i])
                valid_avg_prices.append(avg_prices[i])
            except ValueError:
                # 如果时间不在列表中，跳过
                continue
        
        x_data = np.array(x_data)
        valid_prices = np.array(valid_prices)
        valid_avg_prices = np.array(valid_avg_prices)
        
        # 数据平滑处理：使用样条插值生成更多中间点
        if len(x_data) > 3:  # 至少需要4个点才能插值
            # 生成更密集的x坐标（10倍密度）
            x_smooth = np.linspace(x_data.min(), x_data.max(), len(x_data) * 10)
            
            try:
                # 使用三次样条插值平滑价格曲线
                spl_price = make_interp_spline(x_data, valid_prices, k=3)
                prices_smooth = spl_price(x_smooth)
                
                # 平滑均价曲线
                spl_avg = make_interp_spline(x_data, valid_avg_prices, k=3)
                avg_prices_smooth = spl_avg(x_smooth)
            except:
                # 如果插值失败，使用原始数据
                x_smooth = x_data
                prices_smooth = valid_prices
                avg_prices_smooth = valid_avg_prices
        else:
            x_smooth = x_data
            prices_smooth = valid_prices
            avg_prices_smooth = valid_avg_prices
        
        # 绘制昨收价线（虚线）- 横跨全天
        self.timeshare_ax.axhline(y=pre_close, color='gray', linestyle='--', 
                                  linewidth=1, alpha=0.6, label='Pre Close')
        
        # 绘制价格线（使用平滑后的数据）
        price_color = 'red' if current_price >= pre_close else 'green'
        self.timeshare_ax.plot(x_smooth, prices_smooth, color=price_color, 
                              linewidth=2, label='Price', alpha=0.9, antialiased=True)
        
        # 绘制均价线（使用平滑后的数据）
        self.timeshare_ax.plot(x_smooth, avg_prices_smooth, color='#FF8C00', 
                              linewidth=1.5, label='Avg Price', alpha=0.85, 
                              linestyle='-', antialiased=True)
        
        # 填充价格区域（使用平滑后的数据）
        self.timeshare_ax.fill_between(x_smooth, pre_close, prices_smooth, 
                                       where=(prices_smooth >= pre_close), 
                                       color='red', alpha=0.08)
        self.timeshare_ax.fill_between(x_smooth, pre_close, prices_smooth, 
                                       where=(prices_smooth < pre_close), 
                                       color='green', alpha=0.08)
        
        # 固定X轴范围为全天240分钟
        self.timeshare_ax.set_xlim(0, total_minutes - 1)
        
        # 设置X轴刻度（显示关键时间点）
        key_times = [
            (0, '09:30'),
            (30, '10:00'),
            (60, '10:30'),
            (90, '11:00'),
            (119, '11:30'),
            (120, '13:00'),
            (150, '13:30'),
            (180, '14:00'),
            (210, '14:30'),
            (239, '15:00')
        ]
        
        x_ticks = [t[0] for t in key_times]
        x_labels = [t[1] for t in key_times]
        self.timeshare_ax.set_xticks(x_ticks)
        self.timeshare_ax.set_xticklabels(x_labels, rotation=45, fontsize=9)
        
        # 设置Y轴
        self.timeshare_ax.set_ylabel('Price (CNY)', fontsize=9)
        
        # 添加价格信息框
        info_text = (
            f'Current: {current_price:.2f}\n'
            f'Change: {change_pct:+.2f}%\n'
            f'Pre Close: {pre_close:.2f}\n'
            f'Avg: {avg_prices[-1]:.2f}'
        )
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.85)
        self.timeshare_ax.text(0.02, 0.98, info_text, transform=self.timeshare_ax.transAxes, 
                              fontsize=9, verticalalignment='top', bbox=props,
                              family='monospace')
        
        # 设置网格（更细腻的网格）
        self.timeshare_ax.grid(True, alpha=0.25, linestyle='--', linewidth=0.5)
        
        # 添加图例
        self.timeshare_ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
        
        # 优化显示范围（留出适当边距）
        y_min = min(prices_smooth.min(), avg_prices_smooth.min(), pre_close)
        y_max = max(prices_smooth.max(), avg_prices_smooth.max(), pre_close)
        y_margin = (y_max - y_min) * 0.05  # 5%边距
        self.timeshare_ax.set_ylim(y_min - y_margin, y_max + y_margin)
        
        # 设置边距
        self.timeshare_figure.subplots_adjust(
            top=0.95, bottom=0.12, left=0.08, right=0.98
        )
    
    def load_kline_chart(self, stock_code):
        """加载K线图"""
        from data.fetchers.kline_fetcher import KLineFetcher
        
        # 检查缓存
        if stock_code in self.kline_cache:
            self._render_kline_from_cache(stock_code)
            return
        
        self.log_message(f"📊 正在加载 {stock_code} 的K线图...")
        
        try:
            # 获取K线数据（获取更多数据以便计算均线）
            fetcher = KLineFetcher()
            df = fetcher.get_kline_data(stock_code, count=120)
            
            if df is None or df.empty:
                self.log_message(f"❌ 无法获取 {stock_code} 的K线数据")
                return
            
            # 计算均线
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            
            # 计算MACD
            df = self.calculate_macd(df)
            
            # 缓存K线数据
            self.kline_cache[stock_code] = df
            
            # 清空之前的图表
            self.ax.clear()
            self.ax_volume.clear()  # 清空成交量
            self.ax_macd.clear()
            
            # 绘制K线图
            stock_name = self.quote_cache.get(stock_code, {}).get('name', stock_code)
            
            # 使用matplotlib绘制K线图和均线
            self.plot_kline_with_ma(df, stock_code, stock_name)
            
            self.canvas.draw_idle()  # 使用异步绘制，避免卡顿
            self.log_message(f"✅ {stock_code} K线图加载成功")
            
        except Exception as e:
            self.log_message(f"❌ 加载K线图失败: {str(e)}")
            print(f"K线图错误: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_current_kline(self):
        """刷新当前显示的K线图（仅在交易时段）"""
        current_row = self.stock_table.currentRow()
        if current_row < 0 or current_row >= len(self.stock_list):
            return
        
        stock_code = self.stock_list[current_row]
        
        # 检查是否在交易时段或收盘后15分钟内
        from datetime import time
        now = datetime.now()
        current_time = now.time()
        
        is_trading = (
            (time(9, 30) <= current_time <= time(11, 30)) or
            (time(13, 0) <= current_time <= time(15, 0))
        )
        is_after_close = time(15, 0) <= current_time <= time(15, 15)
        
        if is_trading or is_after_close:
            # 清除缓存，强制重新获取数据
            if stock_code in self.kline_cache:
                del self.kline_cache[stock_code]
            
            self.log_message(f"🔄 自动刷新 {stock_code} K线图...")
            self.load_kline_chart(stock_code)
    
    def refresh_current_timeshare(self):
        """刷新当前显示的分时图（仅在交易时段）- 优化版"""
        current_row = self.stock_table.currentRow()
        if current_row < 0 or current_row >= len(self.stock_list):
            return
        
        stock_code = self.stock_list[current_row]
        
        # 检查是否在交易时段
        from datetime import time
        now = datetime.now()
        current_time = now.time()
        
        is_trading = (
            (time(9, 30) <= current_time <= time(11, 30)) or
            (time(13, 0) <= current_time <= time(15, 0))
        )
        
        if is_trading:
            # 清除缓存，强制重新获取数据
            if stock_code in self.timeshare_cache:
                del self.timeshare_cache[stock_code]
            
            # 静默刷新，不记录日志，使用优化的绘制方式
            self.load_timeshare_chart(stock_code, silent=True, fast_update=True)
    
    def on_height_ratio_changed(self, ratio_text):
        """当高度比例改变时重新绘制图表"""
        # 解析比例文本，如 "3:1" -> [3, 1]
        ratios = [int(x) for x in ratio_text.split(':')]
        
        # 清除旧的子图
        self.figure.clear()
        
        # 重新创建GridSpec和子图（3个子图：K线、成交量、MACD）
        from matplotlib.gridspec import GridSpec
        # 如果只提供了2个比例，自动添加成交量和MACD的比例
        if len(ratios) == 2:
            # 将原来的MACD比例分配给成交量和MACD
            ratios = [ratios[0], 1, 1]
        elif len(ratios) != 3:
            ratios = [4, 1, 1]  # 默认比例
        
        self.gs = GridSpec(3, 1, figure=self.figure, height_ratios=ratios, hspace=0.05)
        self.ax = self.figure.add_subplot(self.gs[0])  # K线图
        self.ax_volume = self.figure.add_subplot(self.gs[1])  # 成交量
        self.ax_macd = self.figure.add_subplot(self.gs[2])  # MACD
        
        # 设置边距
        self.figure.subplots_adjust(
            top=0.97, bottom=0.035, left=0.065, right=0.99
        )
        
        # 如果有当前选中的股票，重新绘制
        current_row = self.stock_table.currentRow()
        if current_row >= 0 and current_row < len(self.stock_list):
            stock_code = self.stock_list[current_row]
            if stock_code in self.kline_cache:
                self._render_kline_from_cache(stock_code)
        
        # 重新绘制
        self.canvas.draw_idle()  # 使用异步绘制，避免卡顿
        self.log_message(f"📐 K线高度比例已调整为 {ratio_text}")
    
    def calculate_macd(self, df):
        """计算MACD指标"""
        # 计算EMA
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # 计算DIF (MACD线)
        df['dif'] = df['ema12'] - df['ema26']
        
        # 计算DEA (信号线)
        df['dea'] = df['dif'].ewm(span=9, adjust=False).mean()
        
        # 计算MACD柱 (histogram)
        df['macd'] = (df['dif'] - df['dea']) * 2
        
        return df
    
    def plot_kline_with_ma(self, df, stock_code, stock_name):
        """绘制K线图、成交量和均线"""
        import numpy as np
        import matplotlib.pyplot as plt
        from datetime import time
        
        # 设置标题
        self.ax.set_title(f'{stock_code} - Daily K-Line', fontsize=14, pad=10)
        
        # 准备数据
        dates = df['day'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        ma5 = df['ma5'].values
        ma10 = df['ma10'].values
        ma20 = df['ma20'].values
        
        # 获取实时价格和涨幅（如果有缓存）
        current_price = closes[-1]
        price_label = 'Close'
        use_realtime = False
        change_pct = 0  # 涨跌幅
        
        if stock_code in self.quote_cache:
            quote = self.quote_cache[stock_code]
            realtime_price = quote.get('price', 0)
            change_pct = quote.get('change_pct', 0)  # 从缓存获取涨跌幅
            
            # 判断是否在交易时段
            now = datetime.now()
            current_time = now.time()
            is_trading = (
                (time(9, 30) <= current_time <= time(11, 30)) or
                (time(13, 0) <= current_time <= time(15, 0))
            )
            
            if realtime_price > 0:
                current_price = realtime_price
                price_label = 'Real-time' if is_trading else 'Latest'
                use_realtime = is_trading
        
        # 获取历史均线（最后一个有效值）
        static_ma5 = df['ma5'].dropna().iloc[-1] if not df['ma5'].dropna().empty else 0
        static_ma10 = df['ma10'].dropna().iloc[-1] if not df['ma10'].dropna().empty else 0
        static_ma20 = df['ma20'].dropna().iloc[-1] if not df['ma20'].dropna().empty else 0
        
        # 计算动态均线（包含实时价格）
        if use_realtime:
            closes_list = list(closes)
            closes_list[-1] = current_price
            
            live_ma5 = np.mean(closes_list[-5:]) if len(closes_list) >= 5 else static_ma5
            live_ma10 = np.mean(closes_list[-10:]) if len(closes_list) >= 10 else static_ma10
            live_ma20 = np.mean(closes_list[-20:]) if len(closes_list) >= 20 else static_ma20
        else:
            live_ma5 = static_ma5
            live_ma10 = static_ma10
            live_ma20 = static_ma20
        
        # 绘制K线
        for i in range(len(df)):
            color = 'red' if closes[i] >= opens[i] else 'green'
            
            # 绘制影线
            self.ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=0.5)
            
            # 绘制实体
            height = abs(closes[i] - opens[i]) or 0.01  # 避免高度为0
            bottom = min(opens[i], closes[i])
            self.ax.bar(i, height, bottom=bottom, color=color, width=0.6, alpha=0.8)
        
        # 绘制均线
        x_range = range(len(df))
        self.ax.plot(x_range, ma5, color='blue', linewidth=1.5, alpha=0.8)
        self.ax.plot(x_range, ma10, color='orange', linewidth=1.5, alpha=0.8)
        self.ax.plot(x_range, ma20, color='purple', linewidth=1.5, alpha=0.8)
        
        # 如果有实时价格，绘制实时价格线
        if use_realtime and current_price != closes[-1]:
            self.ax.axhline(y=current_price, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        
        # 在左上角添加价格信息框
        if use_realtime:
            info_text = (
                f'{price_label}: {current_price:.2f} ({change_pct:+.2f}%)\n'
                f'─────────────────\n'
                f'MA5:  {static_ma5:.2f} → {live_ma5:.2f}\n'
                f'MA10: {static_ma10:.2f} → {live_ma10:.2f}\n'
                f'MA20: {static_ma20:.2f} → {live_ma20:.2f}\n'
                f'(Static → Live)'
            )
        else:
            info_text = (
                f'{price_label}: {current_price:.2f} ({change_pct:+.2f}%)\n'
                f'─────────────────\n'
                f'MA5:  {static_ma5:.2f}\n'
                f'MA10: {static_ma10:.2f}\n'
                f'MA20: {static_ma20:.2f}'
            )
        
        # 添加文本框
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.85)
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes, 
                    fontsize=11, verticalalignment='top', bbox=props,
                    family='monospace')
        
        # 设置X轴
        step = max(1, len(dates) // 10)
        x_ticks = range(0, len(dates), step)
        x_labels = [pd.to_datetime(dates[i]).strftime('%m-%d') for i in x_ticks]
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels([])  # K线图不显示X轴标签
        
        # 设置Y轴
        self.ax.set_ylabel('Price (CNY)', fontsize=10)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        
        # ========== 绘制成交量 ==========
        # 检查DataFrame中是否有volume列
        if 'volume' not in df.columns:
            self.ax_volume.text(0.5, 0.5, 'No volume column in data', 
                               ha='center', va='center', fontsize=10)
            self.ax_volume.set_ylabel('Volume', fontsize=9)
            self.ax_volume.grid(True, alpha=0.3, linestyle='--')
            self.ax_volume.set_xticks(x_ticks)
            self.ax_volume.set_xticklabels([])
        else:
            volumes = df['volume'].values
            
            # 检查成交量数据
            if len(volumes) == 0 or volumes.max() == 0:
                # 如果没有成交量数据，显示提示
                self.ax_volume.text(0.5, 0.5, 'No volume data', 
                                   ha='center', va='center', fontsize=10)
            else:
                # 成交量柱状图颜色（红涨绿跌）
                volume_colors = ['red' if closes[i] >= opens[i] else 'green' for i in range(len(df))]
                self.ax_volume.bar(x_range, volumes, color=volume_colors, alpha=0.6, width=0.6)
                
                # 格式化Y轴刻度（显示为万、亿）- 使用英文避免乱码
                max_volume = volumes.max()
                if max_volume > 100000000:  # 大于1亿
                    self.ax_volume.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/100000000:.1f}E'))
                elif max_volume > 10000:  # 大于1万
                    self.ax_volume.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/10000:.0f}W'))
            
            # 设置成交量Y轴（使用英文）
            self.ax_volume.set_ylabel('Vol', fontsize=9)
            self.ax_volume.grid(True, alpha=0.3, linestyle='--')
            self.ax_volume.set_xticks(x_ticks)
            self.ax_volume.set_xticklabels([])  # 成交量不显示X轴标签
        
        # ========== 绘制MACD ==========
        dif = df['dif'].values
        dea = df['dea'].values
        macd = df['macd'].values
        
        # 绘制MACD柱状图
        colors = ['red' if m >= 0 else 'green' for m in macd]
        self.ax_macd.bar(x_range, macd, color=colors, alpha=0.6, width=0.6)
        
        # 绘制DIF和DEA线
        self.ax_macd.plot(x_range, dif, color='blue', linewidth=1.5, label='DIF', alpha=0.8)
        self.ax_macd.plot(x_range, dea, color='orange', linewidth=1.5, label='DEA', alpha=0.8)
        
        # 绘制零轴线
        self.ax_macd.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
        
        # 设置MACD的X轴（显示日期）
        self.ax_macd.set_xticks(x_ticks)
        self.ax_macd.set_xticklabels(x_labels, rotation=45)
        
        # 设置MACD的Y轴
        self.ax_macd.set_ylabel('MACD', fontsize=10)
        self.ax_macd.grid(True, alpha=0.3, linestyle='--')
        self.ax_macd.legend(loc='upper left', fontsize=8)
        
        # 设置边距
        self.figure.subplots_adjust(
            top=0.97, bottom=0.035, left=0.065, right=0.99
        )
    
    def add_stock(self):
        """添加股票到显示列表"""
        stock_code = self.stock_input.text().strip()
        
        if not stock_code:
            self.log_message("⚠️ 请输入股票代码")
            return
        
        if stock_code in self.stock_list:
            self.log_message(f"⚠️ 股票 {stock_code} 已存在")
            return
        
        try:
            # 添加到列表
            self.stock_list.append(stock_code)
            
            # 保存到文件
            self.save_stock_list()
            
            # 更新表格显示
            self.update_display()
            
            # 清空输入框
            self.stock_input.clear()
            
            # 记录日志
            self.log_message(f"✅ 已添加股票：{stock_code}")
            
            # 立即获取一次行情
            self.refresh_quotes()
            
        except Exception as e:
            self.log_message(f"❌ 添加股票失败: {str(e)}")
    
    def refresh_quotes(self):
        """刷新所有股票行情（使用线程池优化）"""
        if not self.stock_list:
            return
        
        # 记录开始时间
        from datetime import datetime
        self.refresh_start_time = datetime.now()
        
        # 获取当前可见的股票（优先刷新）
        visible_codes = self._get_visible_stock_codes()
        
        # 使用行情管理器批量获取
        self.quote_manager.fetch_quotes(self.stock_list, priority_codes=visible_codes)
        
        # 只在手动刷新时显示日志
        # 自动刷新时不显示，避免刷屏
    
    def _get_visible_stock_codes(self):
        """获取当前可见的股票代码（用于优先刷新）"""
        visible_codes = []
        
        # 获取表格可见行范围
        if hasattr(self, 'stock_table'):
            first_visible = self.stock_table.rowAt(0)
            last_visible = self.stock_table.rowAt(self.stock_table.height())
            
            if first_visible >= 0 and last_visible >= 0:
                for row in range(first_visible, min(last_visible + 1, len(self.stock_list))):
                    if row < len(self.stock_list):
                        visible_codes.append(self.stock_list[row])
        
        return visible_codes if visible_codes else self.stock_list[:20]  # 默认前20个
    
    def on_batch_progress(self, completed, total):
        """批次进度更新"""
        progress = int(completed / total * 100)
        
        # 更新线程状态显示
        active_threads = self.quote_manager.get_active_count()
        max_threads = self.quote_manager.get_max_thread_count()
        if hasattr(self, 'thread_status_label'):
            self.thread_status_label.setText(f"线程: {active_threads:02d}/{max_threads:02d}")
    
    def on_all_quotes_completed(self):
        """所有行情获取完成"""
        if self.refresh_start_time:
            from datetime import datetime
            elapsed = (datetime.now() - self.refresh_start_time).total_seconds()
            # 只在耗时较长时记录日志
            if elapsed > 2.0:
                self.log_message(f"✅ 行情刷新完成，耗时: {elapsed:.2f}秒")
            self.refresh_start_time = None
    
    def on_quote_ready(self, quote):
        """处理获取到的行情数据"""
        stock_code = quote['code']
        self.quote_cache[stock_code] = quote
        
        # 只在有错误时记录日志，减少日志刷屏
        if quote.get('error'):
            self.log_message(f"❌ {stock_code} ({quote.get('name', '未知')}): {quote['error']}")
        
        # 更新显示
        self.update_display()
    
    def update_display(self):
        """更新行情显示"""
        self.stock_table.setRowCount(len(self.stock_list))
        
        for row, stock_code in enumerate(self.stock_list):
            if stock_code in self.quote_cache:
                quote = self.quote_cache[stock_code]
                
                # 判断是否为指数
                is_index = stock_code in ['999999', '399001', '399006']  # 上证、深证成指、创业板指
                
                # 代码
                code_item = QTableWidgetItem(quote['code'])
                code_item.setTextAlignment(Qt.AlignCenter)
                self.stock_table.setItem(row, 0, code_item)
                
                # 名称
                name_item = QTableWidgetItem(quote['name'])
                name_item.setTextAlignment(Qt.AlignCenter)
                self.stock_table.setItem(row, 1, name_item)
                
                # 涨幅%
                change_pct = quote['change_pct']
                change_pct_item = QTableWidgetItem(f"{change_pct:+.2f}%")
                change_pct_item.setTextAlignment(Qt.AlignCenter)
                if change_pct > 0:
                    change_pct_item.setForeground(QColor(255, 0, 0))  # 红色
                elif change_pct < 0:
                    change_pct_item.setForeground(QColor(0, 128, 0))  # 绿色
                self.stock_table.setItem(row, 2, change_pct_item)
                
                # 现价
                price_item = QTableWidgetItem(f"{quote['price']:.2f}")
                price_item.setTextAlignment(Qt.AlignCenter)
                if change_pct > 0:
                    price_item.setForeground(QColor(255, 0, 0))
                elif change_pct < 0:
                    price_item.setForeground(QColor(0, 128, 0))
                self.stock_table.setItem(row, 3, price_item)
                
                # 涨跌
                change_item = QTableWidgetItem(f"{quote['change']:+.2f}")
                change_item.setTextAlignment(Qt.AlignCenter)
                if quote['change'] > 0:
                    change_item.setForeground(QColor(255, 0, 0))
                elif quote['change'] < 0:
                    change_item.setForeground(QColor(0, 128, 0))
                self.stock_table.setItem(row, 4, change_item)
                
                # 总市值（亿）- 指数显示"-"
                if is_index:
                    market_cap_text = "-"
                else:
                    market_cap = quote.get('market_cap', 0)
                    market_cap_text = f"{market_cap:.2f}亿" if market_cap > 0 else "-"
                market_cap_item = QTableWidgetItem(market_cap_text)
                market_cap_item.setTextAlignment(Qt.AlignCenter)
                self.stock_table.setItem(row, 5, market_cap_item)
                
                # 流通值（亿）- 指数显示"-"
                if is_index:
                    circulation_text = "-"
                else:
                    circulation = quote.get('circulation', 0)
                    circulation_text = f"{circulation:.2f}亿" if circulation > 0 else "-"
                circulation_item = QTableWidgetItem(circulation_text)
                circulation_item.setTextAlignment(Qt.AlignCenter)
                self.stock_table.setItem(row, 6, circulation_item)
                
                # 振幅%
                amplitude = quote.get('amplitude', 0)
                if amplitude > 0:
                    amplitude_text = f"{amplitude:.2f}%"
                else:
                    # 计算振幅 = (最高-最低)/昨收*100
                    if quote['pre_close'] > 0:
                        amplitude = (quote['high'] - quote['low']) / quote['pre_close'] * 100
                        amplitude_text = f"{amplitude:.2f}%"
                    else:
                        amplitude_text = "-"
                amplitude_item = QTableWidgetItem(amplitude_text)
                amplitude_item.setTextAlignment(Qt.AlignCenter)
                self.stock_table.setItem(row, 7, amplitude_item)
            else:
                # 显示加载中
                for col in range(8):
                    item = QTableWidgetItem("加载中..." if col == 1 else "-")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.stock_table.setItem(row, col, item)
    
    def log_message(self, message):
        """输出日志消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_text = f"[{timestamp}] {message}"
        
        if hasattr(self, 'log_content'):
            self.log_content.append(log_text)
    
    def create_middle_widget(self):
        """创建中间区域（分时图和AI区域）"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 创建上下分割器
        middle_splitter = QSplitter(Qt.Vertical)
        
        # 上部分：分时图
        timeshare_widget = self.create_timeshare_widget()
        middle_splitter.addWidget(timeshare_widget)
        
        # 下部分：AI区域
        ai_widget = self.create_ai_widget()
        middle_splitter.addWidget(ai_widget)
        
        # 调整上下比例 - 分时图占3份，AI区域占2份（让AI区域底部和K线图底部对齐）
        middle_splitter.setStretchFactor(0, 3)
        middle_splitter.setStretchFactor(1, 2)
        
        layout.addWidget(middle_splitter)
        
        return widget
    
    def create_timeshare_widget(self):
        """创建分时图区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        label = QLabel("📈 分时图")
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        label.setFixedHeight(40)
        layout.addWidget(label)
        
        # 分时图内容区域
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        
        self.timeshare_figure = Figure(figsize=(6, 4))
        self.timeshare_canvas = FigureCanvas(self.timeshare_figure)
        self.timeshare_ax = self.timeshare_figure.add_subplot(111)
        
        # 设置边距
        self.timeshare_figure.subplots_adjust(
            top=0.95, bottom=0.08, left=0.08, right=0.98
        )
        
        # 初始化空图表
        self.timeshare_ax.text(0.5, 0.5, 'Click a stock to view timeshare chart', 
                              ha='center', va='center', fontsize=11, family='sans-serif')
        self.timeshare_ax.set_xticks([])
        self.timeshare_ax.set_yticks([])
        
        layout.addWidget(self.timeshare_canvas)
        
        return widget
    
    def create_ai_widget(self):
        """创建AI区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        label = QLabel("🤖 AI分析")
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        label.setFixedHeight(40)
        layout.addWidget(label)
        
        # AI对话历史区域（只读）
        self.ai_chat_history = QTextEdit()
        self.ai_chat_history.setPlaceholderText("AI对话将显示在这里...\n\n提示：\n- 输入问题后按回车或点击发送\n- 可以询问股票分析、技术指标等")
        self.ai_chat_history.setReadOnly(True)
        self.ai_chat_history.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        # 设置样式
        self.ai_chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.ai_chat_history)
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)
        
        # 输入框 - 使用QTextEdit代替QLineEdit以获得更好的输入法支持
        # QTextEdit对fcitx5的支持比QLineEdit更好，特别是在某些桌面环境下
        from PyQt5.QtWidgets import QTextEdit as QTextEditInput
        self.ai_input = QTextEditInput()
        self.ai_input.setPlaceholderText("输入您的问题...")
        self.ai_input.setMaximumHeight(64)  # 设置为64px
        self.ai_input.setMinimumHeight(64)  # 设置为64px
        # 强制启用输入法支持
        self.ai_input.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.ai_input.setAcceptRichText(False)  # 只接受纯文本
        # 设置焦点策略
        self.ai_input.setFocusPolicy(Qt.StrongFocus)
        self.ai_input.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        
        # 处理回车键发送（Shift+Enter换行，Enter发送）
        def handle_key_press(event):
            from PyQt5.QtCore import Qt as QtCore
            from PyQt5.QtGui import QKeyEvent
            if event.key() == QtCore.Key_Return and not (event.modifiers() & QtCore.ShiftModifier):
                self.send_ai_message()
                event.accept()
            else:
                QTextEditInput.keyPressEvent(self.ai_input, event)
        
        self.ai_input.keyPressEvent = handle_key_press
        input_layout.addWidget(self.ai_input)
        
        # 发送按钮
        send_button = QPushButton("发送")
        send_button.clicked.connect(self.send_ai_message)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        send_button.setFixedWidth(80)
        input_layout.addWidget(send_button)
        
        # 清空按钮
        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear_ai_chat)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c41700;
            }
        """)
        clear_button.setFixedWidth(80)
        input_layout.addWidget(clear_button)
        
        # AI服务启动按钮
        self.ai_service_button = QPushButton("启动AI")
        self.ai_service_button.clicked.connect(self.toggle_ai_service)
        self.ai_service_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        self.ai_service_button.setFixedWidth(80)
        input_layout.addWidget(self.ai_service_button)
        
        # 更新AI服务按钮状态
        self.update_ai_service_button()
        
        layout.addLayout(input_layout)
        
        # 初始化AI对话历史
        self.ai_messages = []
        
        return widget
    
    def send_ai_message(self):
        """发送AI消息"""
        message = self.ai_input.toPlainText().strip()  # 使用toPlainText()代替text()
        
        if not message:
            return
        
        # 清空输入框
        self.ai_input.clear()
        
        # 添加用户消息到历史
        self.add_ai_message("user", message)
        
        # 显示"正在思考"提示
        self.add_ai_message("ai", "正在思考...")
        
        # 获取当前选中的股票
        current_row = self.stock_table.currentRow()
        current_stock = None
        if current_row >= 0 and current_row < len(self.stock_list):
            stock_code = self.stock_list[current_row]
            stock_name = self.quote_cache.get(stock_code, {}).get('name', stock_code)
            current_stock = f"{stock_name}({stock_code})"
        
        # 异步生成AI回复
        self.generate_ai_response_async(message, current_stock)
    
    def add_ai_message(self, sender, message):
        """添加消息到AI对话历史"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # 保存到消息历史
        self.ai_messages.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        })
        
        # 更新显示
        self.update_ai_chat_display()
    
    def update_ai_chat_display(self):
        """更新AI对话显示"""
        html_content = """
        <style>
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 8px;
                max-width: 85%;
            }
            .user-message {
                background-color: #e3f2fd;
                margin-left: auto;
                text-align: right;
                border: 1px solid #90caf9;
            }
            .ai-message {
                background-color: #f1f8e9;
                margin-right: auto;
                text-align: left;
                border: 1px solid #aed581;
            }
            .system-message {
                background-color: #ffebee;
                margin-left: auto;
                margin-right: auto;
                text-align: left;
                border: 2px solid #ff0000;
                max-width: 95%;
                font-family: monospace;
                font-size: 12px;
                white-space: pre-wrap;
            }
            .timestamp {
                font-size: 11px;
                color: #666;
                margin-top: 5px;
            }
            .sender {
                font-weight: bold;
                margin-bottom: 5px;
            }
            .user-sender {
                color: #1976d2;
            }
            .ai-sender {
                color: #558b2f;
            }
            .system-sender {
                color: #cc0000;
            }
        </style>
        """
        
        for msg in self.ai_messages:
            if msg['sender'] == "system":
                # 系统消息（股票信息）
                html_content += f"""
                <div class="message system-message">
                    <div class="sender system-sender">📊 系统信息</div>
                    <div>{msg['message']}</div>
                    <div class="timestamp">{msg['timestamp']}</div>
                </div>
                """
            else:
                # 用户或AI消息
                sender_class = "user" if msg['sender'] == "user" else "ai"
                sender_name = "您" if msg['sender'] == "user" else "AI助手"
                sender_emoji = "👤" if msg['sender'] == "user" else "🤖"
                
                html_content += f"""
                <div class="message {sender_class}-message">
                    <div class="sender {sender_class}-sender">{sender_emoji} {sender_name}</div>
                    <div>{msg['message']}</div>
                    <div class="timestamp">{msg['timestamp']}</div>
                </div>
                """
        
        self.ai_chat_history.setHtml(html_content)
        
        # 滚动到顶部
        scrollbar = self.ai_chat_history.verticalScrollBar()
        scrollbar.setValue(0)
    
    def clear_ai_chat(self):
        """清空AI对话历史"""
        self.ai_messages = []
        self.ai_chat_history.clear()
        self.ai_chat_history.setPlaceholderText("AI对话将显示在这里...\n\n提示：\n- 输入问题后按回车或点击发送\n- 可以询问股票分析、技术指标等")
        self.log_message("🗑️ 已清空AI对话历史")
    
    def update_ai_service_button(self):
        """更新AI服务按钮状态"""
        if hasattr(self, 'use_real_ai') and self.use_real_ai:
            self.ai_service_button.setText("停止AI")
            self.ai_service_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 8px 20px;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
        else:
            self.ai_service_button.setText("启动AI")
            self.ai_service_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    padding: 8px 20px;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
                QPushButton:pressed {
                    background-color: #E65100;
                }
            """)
    
    def toggle_ai_service(self):
        """启动或停止AI服务"""
        import subprocess
        import time
        
        if hasattr(self, 'use_real_ai') and self.use_real_ai:
            # 停止AI服务
            try:
                subprocess.run(['pkill', '-f', 'ollama serve'], check=False)
                self.use_real_ai = False
                self.update_ai_service_button()
                self.log_message("🛑 AI服务已停止")
                self.add_ai_message("system", "AI服务已停止")
            except Exception as e:
                self.log_message(f"⚠️ 停止AI服务失败: {e}")
        else:
            # 启动AI服务
            try:
                self.log_message("🚀 正在启动AI服务...")
                self.add_ai_message("system", "正在启动AI服务，请稍候...")
                
                # 后台启动ollama服务
                subprocess.Popen(
                    ['nohup', 'ollama', 'serve'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                
                # 等待服务启动（最多等待5秒）
                for i in range(10):
                    time.sleep(0.5)
                    try:
                        from ai.llm_client import LLMClient
                        client = LLMClient()
                        status, msg = client.check_status()
                        if status:
                            self.llm_client = client
                            self.use_real_ai = True
                            self.update_ai_service_button()
                            self.log_message(f"✅ AI服务启动成功: {msg}")
                            self.add_ai_message("system", f"AI服务启动成功！{msg}")
                            return
                    except:
                        pass
                
                # 超时
                self.log_message("⚠️ AI服务启动超时，请手动检查")
                self.add_ai_message("system", "AI服务启动超时，请在终端运行: ollama serve")
                
            except Exception as e:
                self.log_message(f"⚠️ 启动AI服务失败: {e}")
                self.add_ai_message("system", f"启动失败: {e}\n请在终端运行: ollama serve")
    
    def generate_ai_response_async(self, message, current_stock):
        """异步生成AI回复（不阻塞UI）"""
        
        # 如果有真实AI，使用大模型（异步）
        if hasattr(self, 'use_real_ai') and self.use_real_ai:
            self._generate_real_ai_response_async(message, current_stock)
        else:
            # 降级到模拟回复（同步，很快）
            ai_response = self._generate_mock_response(message, current_stock)
            # 移除"正在思考"，添加真实回复
            self.ai_messages.pop()  # 移除最后一条"正在思考"
            self.add_ai_message("ai", ai_response)
            self.log_message(f"💬 AI对话: {message[:30]}...")
    
    def _generate_real_ai_response_async(self, message, current_stock):
        """使用真实大模型生成回复（异步）"""
        try:
            # 构建上下文 - 包含实时行情数据
            context = self._build_stock_context(message, current_stock)
            
            # 创建工作线程
            self.ai_worker = AIWorkerThread(
                self.llm_client,
                message,
                self.stock_analysis_prompt,
                context
            )
            
            # 连接完成信号
            self.ai_worker.finished.connect(self._on_ai_response_ready)
            
            # 启动线程
            self.ai_worker.start()
            
            # 记录日志
            self.log_message(f"💬 AI对话: {message[:30]}... (后台处理中)")
            
        except Exception as e:
            # 移除"正在思考"
            self.ai_messages.pop()
            error_msg = f"AI服务错误: {str(e)}"
            self.add_ai_message("ai", error_msg)
    
    def _build_stock_context(self, message, current_stock):
        """构建股票上下文信息"""
        context = "【重要】以下是实时行情数据，请基于这些真实数据进行分析：\n\n"
        
        # 检查用户是否询问特定股票
        mentioned_codes = []
        for stock_code in self.stock_list:
            if stock_code in message:
                mentioned_codes.append(stock_code)
        
        # 如果用户提到了具体股票代码，提供该股票信息
        if mentioned_codes:
            for stock_code in mentioned_codes:
                if stock_code in self.quote_cache:
                    quote = self.quote_cache[stock_code]
                    context += f"""
股票代码：{stock_code}
股票名称：{quote['name']}
实时数据（来自程序实时获取）：
- 现价：{quote['price']:.2f}元
- 涨跌幅：{quote['change_pct']:+.2f}%
- 涨跌额：{quote['change']:+.2f}元
- 昨收价：{quote['pre_close']:.2f}元
- 今日最高：{quote['high']:.2f}元
- 今日最低：{quote['low']:.2f}元
- 开盘价：{quote['open']:.2f}元
"""
                    # 添加市值信息（如果不是指数）
                    if stock_code not in ['999999', '399001', '399006']:
                        market_cap = quote.get('market_cap', 0)
                        circulation = quote.get('circulation', 0)
                        if market_cap > 0:
                            context += f"- 总市值：{market_cap:.2f}亿元\n"
                        if circulation > 0:
                            context += f"- 流通市值：{circulation:.2f}亿元\n"
                    
                    context += "\n"
        
        # 如果用户询问"行情列表"或"所有股票"，提供列表摘要
        elif any(keyword in message for keyword in ['行情列表', '所有股票', '列表', '这些股票', '全部']):
            context += "当前行情列表中的股票（实时数据）：\n\n"
            for stock_code in self.stock_list[:10]:  # 限制前10只，避免太长
                if stock_code in self.quote_cache:
                    quote = self.quote_cache[stock_code]
                    context += f"{stock_code} {quote['name']}: {quote['price']:.2f}元 ({quote['change_pct']:+.2f}%)\n"
            
            if len(self.stock_list) > 10:
                context += f"\n...还有{len(self.stock_list)-10}只股票\n"
            
            context += "\n"
        
        # 如果有当前选中的股票，也提供其信息
        elif current_stock:
            stock_code = current_stock.split('(')[1].rstrip(')')
            if stock_code in self.quote_cache:
                quote = self.quote_cache[stock_code]
                context += f"""
当前选中股票：{current_stock}
实时数据（来自程序实时获取）：
- 现价：{quote['price']:.2f}元
- 涨跌幅：{quote['change_pct']:+.2f}%
- 涨跌额：{quote['change']:+.2f}元
- 昨收价：{quote['pre_close']:.2f}元
- 今日最高：{quote['high']:.2f}元
- 今日最低：{quote['low']:.2f}元
- 开盘价：{quote['open']:.2f}元
"""
        
        context += "\n请基于以上实时数据进行分析，不要使用你训练数据中的过时信息。"
        return context
    
    def _on_ai_response_ready(self, response):
        """AI回复准备好时的回调"""
        # 移除"正在思考"消息
        if self.ai_messages and self.ai_messages[-1]['message'] == "正在思考...":
            self.ai_messages.pop()
        
        # 添加真实回复
        self.add_ai_message("ai", response)
    
    def generate_ai_response(self, message, current_stock):
        """生成AI回复（保留用于兼容，实际使用异步版本）"""
        # 这个方法保留用于兼容，实际调用已改为异步
        return self._generate_mock_response(message, current_stock)
    
    def _generate_mock_response(self, message, current_stock):
        """生成模拟回复（降级方案）"""
        message_lower = message.lower()
        
        # 如果有当前股票，获取相关数据
        stock_info = ""
        if current_stock:
            stock_code = current_stock.split('(')[1].rstrip(')')
            if stock_code in self.quote_cache:
                quote = self.quote_cache[stock_code]
                stock_info = f"\n\n当前股票：{current_stock}\n"
                stock_info += f"现价：{quote['price']:.2f}元\n"
                stock_info += f"涨跌幅：{quote['change_pct']:+.2f}%\n"
                stock_info += f"涨跌额：{quote['change']:+.2f}元"
        
        # 简单的关键词匹配回复
        if "分析" in message_lower or "怎么样" in message_lower:
            if current_stock:
                return f"正在分析 {current_stock}...{stock_info}\n\n基于当前数据，该股票呈现{'上涨' if self.quote_cache.get(stock_code, {}).get('change_pct', 0) > 0 else '下跌'}趋势。\n\n💡 提示：这是模拟回复，实际应接入真实AI分析引擎。"
            else:
                return "请先在行情表格中选择一只股票，然后我可以为您分析。"
        
        elif "买" in message_lower or "卖" in message_lower:
            return f"⚠️ 投资有风险，入市需谨慎！\n\n我是AI助手，只能提供参考信息，不构成投资建议。请根据自己的风险承受能力做出决策。{stock_info}"
        
        elif "指标" in message_lower or "macd" in message_lower or "均线" in message_lower:
            if current_stock:
                return f"技术指标分析 - {current_stock}{stock_info}\n\n📊 您可以在右侧K线图中查看：\n- MACD指标\n- MA5/MA10/MA20均线\n- 成交量等信息\n\n💡 提示：这是模拟回复，实际应接入真实技术分析引擎。"
            else:
                return "请先选择一只股票，我可以为您分析技术指标。"
        
        elif "帮助" in message_lower or "功能" in message_lower:
            return """🤖 AI助手功能说明：

1. 股票分析：询问"分析XXX"或"XXX怎么样"
2. 技术指标：询问"MACD"、"均线"等
3. 实时行情：选中股票后自动显示相关信息

💡 提示：
- 当前为演示版本，使用模拟回复
- 实际部署时可接入真实AI分析引擎
- 支持自然语言对话"""
        
        else:
            return f"收到您的消息：{message}\n\n{stock_info if stock_info else ''}\n💡 您可以询问：\n- 股票分析\n- 技术指标\n- 买卖建议\n- 输入\"帮助\"查看更多功能"
    
    def create_chart_widget(self):
        """创建K线图显示区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        label = QLabel("📊 K线图")
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        label.setFixedHeight(40)
        layout.addWidget(label)
        
        # K线图内容区域
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
        from matplotlib.figure import Figure
        
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        # 创建三个子图：上面K线，中间成交量，下面MACD
        # 使用gridspec来控制高度比例
        from matplotlib.gridspec import GridSpec
        self.gs = GridSpec(3, 1, figure=self.figure, height_ratios=[4, 1, 1], hspace=0.05)
        self.ax = self.figure.add_subplot(self.gs[0])  # K线图
        self.ax_volume = self.figure.add_subplot(self.gs[1])  # 成交量
        self.ax_macd = self.figure.add_subplot(self.gs[2])  # MACD
        
        # 设置默认边距：左边留出空间显示价格
        self.figure.subplots_adjust(
            top=0.97, bottom=0.035, left=0.065, right=0.99
        )
        
        # 创建自定义工具栏（中文提示）
        class ChineseNavigationToolbar(NavigationToolbar):
            """中文工具栏"""
            # 重写工具提示文本
            toolitems = (
                ('Home', '复位视图', 'home', 'home'),
                ('Back', '后退', 'back', 'back'),
                ('Forward', '前进', 'forward', 'forward'),
                (None, None, None, None),
                ('Pan', '平移\n左键拖动平移\n右键拖动缩放', 'move', 'pan'),
                ('Zoom', '区域缩放\n框选区域放大', 'zoom_to_rect', 'zoom'),
                (None, None, None, None),
                ('Subplots', '子图配置', 'subplots', 'configure_subplots'),
                ('Save', '保存图片', 'filesave', 'save_figure'),
            )
        
        # 初始化空图表（使用英文避免字体加载问题）
        self.ax.text(0.5, 0.5, 'Click a stock to view K-Line chart', 
                    ha='center', va='center', fontsize=12, family='sans-serif')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        self.ax_volume.text(0.5, 0.5, 'Volume', 
                           ha='center', va='center', fontsize=10, family='sans-serif')
        self.ax_volume.set_xticks([])
        self.ax_volume.set_yticks([])
        
        self.ax_macd.text(0.5, 0.5, 'MACD Indicator', 
                         ha='center', va='center', fontsize=10, family='sans-serif')
        self.ax_macd.set_xticks([])
        self.ax_macd.set_yticks([])
        
        # 先添加canvas
        layout.addWidget(self.canvas)
        
        # 再添加工具栏到底部
        self.toolbar = ChineseNavigationToolbar(self.canvas, widget)
        layout.addWidget(self.toolbar)
        
        # 添加滑块控制K线和MACD的高度比例
        slider_layout = QHBoxLayout()
        slider_label = QLabel("K线高度比例:")
        slider_label.setStyleSheet("font-size: 12px;")
        slider_layout.addWidget(slider_label)
        
        self.height_slider = QComboBox()
        self.height_slider.addItems(['1:1', '2:1', '3:1', '4:1', '5:1', '6:1'])
        self.height_slider.setCurrentText('3:1')
        self.height_slider.currentTextChanged.connect(self.on_height_ratio_changed)
        self.height_slider.setStyleSheet("font-size: 12px;")
        slider_layout.addWidget(self.height_slider)
        slider_layout.addStretch()
        
        layout.addLayout(slider_layout)
        
        return widget
    
    def create_log_widget(self):
        """创建日志输出区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("📋 系统日志")
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(label)
        
        # 日志内容区域
        self.log_content = QTextEdit()
        self.log_content.setPlaceholderText("系统日志输出...")
        self.log_content.setReadOnly(True)
        # 允许选择和复制文本
        self.log_content.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        layout.addWidget(self.log_content)
        
        return widget
    
    def create_trade_widget(self):
        """创建交易界面区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题栏（包含标题和获取信息按钮）
        title_layout = QHBoxLayout()
        
        # 获取信息按钮
        self.fetch_info_btn = QPushButton("📥 获取信息")
        self.fetch_info_btn.setToolTip("获取当前选中股票的公告、新闻等信息")
        self.fetch_info_btn.clicked.connect(self.fetch_stock_info)
        self.fetch_info_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        title_layout.addWidget(self.fetch_info_btn)
        
        # 状态标签
        self.fetch_status_label = QLabel("")
        self.fetch_status_label.setStyleSheet("font-size: 11px; color: #666;")
        title_layout.addWidget(self.fetch_status_label)
        
        # 添加弹簧
        title_layout.addStretch()
        
        # 标题
        label = QLabel("💰 交易操作")
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        title_layout.addWidget(label)
        
        layout.addLayout(title_layout)
        
        # 交易内容区域
        content = QTextEdit()
        content.setPlaceholderText("交易操作界面...")
        layout.addWidget(content)
        
        return widget


def main():
    """主函数"""
    # 在创建QApplication之前，确保环境变量已设置
    import subprocess
    if os.name == 'posix' and 'QT_IM_MODULE' not in os.environ:
        try:
            subprocess.run(['pgrep', '-x', 'fcitx5'], check=True, capture_output=True)
            os.environ['QT_IM_MODULE'] = 'fcitx5'
        except:
            try:
                subprocess.run(['pgrep', '-x', 'fcitx'], check=True, capture_output=True)
                os.environ['QT_IM_MODULE'] = 'fcitx'
            except:
                os.environ['QT_IM_MODULE'] = 'fcitx5'
    
    print(f"QT_IM_MODULE = {os.environ.get('QT_IM_MODULE')}")
    
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    window = TradingPanel()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
