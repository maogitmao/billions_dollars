#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Billions Dollars - 交易控制面板主界面
"""

import sys
import json
import os
from datetime import datetime
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QSplitter, QTextEdit, QLabel, 
    QLineEdit, QPushButton, QListWidget, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QThreadPool
from PyQt5.QtGui import QColor
from data.fetchers.realtime_fetcher import RealtimeFetcher
from quote_worker import QuoteWorker


class TradingPanel(QMainWindow):
    """交易控制面板主窗口"""
    
    def __init__(self):
        super().__init__()
        self.stock_list = []  # 存储添加的股票代码
        self.fetcher = RealtimeFetcher()  # 实时数据获取器
        self.quote_cache = {}  # 缓存行情数据
        self.workers = {}  # 工作线程字典
        # 使用脚本所在目录作为基准路径
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.stock_file = os.path.join(self.base_dir, 'stock_list.json')
        self.init_ui()
        self.load_stock_list()  # 加载保存的股票列表
        self.setup_timer()  # 设置定时刷新
    
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
                    self.update_display()
                    self.refresh_quotes()
                else:
                    print("📂 股票列表为空")
            except Exception as e:
                print(f"⚠️ 加载股票列表失败: {str(e)}")
                self.log_message(f"⚠️ 加载股票列表失败: {str(e)}")
        else:
            print(f"📂 股票列表文件不存在: {self.stock_file}")
    
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
        
        # 停止所有工作线程
        for worker in self.workers.values():
            if worker.isRunning():
                worker.quit()
                worker.wait(1000)  # 等待最多1秒
        
        event.accept()
    
    def setup_timer(self):
        """设置定时器，每3秒刷新一次行情"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_quotes)
        self.timer.start(3000)  # 3秒刷新一次，与同花顺Level-1行情一致
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Billions Dollars - 交易控制面板")
        self.setGeometry(0, 0, 1920, 1080)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建分割器（上下分割）
        main_splitter = QSplitter(Qt.Vertical)
        
        # 上半部分（左右分割）
        top_splitter = QSplitter(Qt.Horizontal)
        
        # 1. 行情显示区域
        market_widget = self.create_market_widget()
        top_splitter.addWidget(market_widget)
        
        # 2. K线图显示区域
        chart_widget = self.create_chart_widget()
        top_splitter.addWidget(chart_widget)
        
        # 设置上半部分比例
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 1)
        
        main_splitter.addWidget(top_splitter)
        
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
        
        # 设置上下比例 - 上半部分占3份，下半部分占1份
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(main_splitter)
    
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
        # 连接点击事件
        self.stock_table.cellClicked.connect(self.on_stock_selected)
        
        layout.addWidget(self.stock_table)
        
        return widget
    
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
                self.stock_list.pop(row)
                self.log_message(f"🗑️ 已删除股票：{stock_code}")
        
        # 保存到文件
        self.save_stock_list()
        
        # 更新显示
        self.update_display()
    
    def manual_refresh(self):
        """手动刷新行情"""
        self.log_message("🔄 手动刷新行情...")
        self.refresh_quotes()
    
    def on_stock_selected(self, row, column):
        """股票被选中时显示K线图"""
        if row < len(self.stock_list):
            stock_code = self.stock_list[row]
            self.log_message(f"� 正在加载 {stock_code} 的K线图...")
            self.load_kline_chart(stock_code)
    
    def load_kline_chart(self, stock_code):
        """加载K线图"""
        from data.fetchers.kline_fetcher import KLineFetcher
        
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
            
            # 清空之前的图表
            self.ax.clear()
            
            # 绘制K线图
            stock_name = self.quote_cache.get(stock_code, {}).get('name', stock_code)
            
            # 使用matplotlib绘制K线图和均线
            self.plot_kline_with_ma(df, stock_code, stock_name)
            
            self.canvas.draw()
            self.log_message(f"✅ {stock_code} K线图加载成功")
            
        except Exception as e:
            self.log_message(f"❌ 加载K线图失败: {str(e)}")
            print(f"K线图错误: {e}")
            import traceback
            traceback.print_exc()
    
    def plot_kline_with_ma(self, df, stock_code, stock_name):
        """绘制K线图和均线"""
        import numpy as np
        from datetime import datetime, time
        
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
        
        # 获取实时价格（如果有缓存）
        current_price = closes[-1]
        price_label = 'Close'
        use_realtime = False
        
        if stock_code in self.quote_cache:
            quote = self.quote_cache[stock_code]
            realtime_price = quote.get('price', 0)
            
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
        
        # 获取历史均线
        static_ma5 = df['ma5'].dropna().iloc[-1] if not df['ma5'].dropna().empty else 0
        static_ma10 = df['ma10'].dropna().iloc[-1] if not df['ma10'].dropna().empty else 0
        static_ma20 = df['ma20'].dropna().iloc[-1] if not df['ma20'].dropna().empty else 0
        
        # 计算动态均线（包含实时价格）
        if use_realtime:
            # 用实时价格替换最后一天的收盘价，然后取最近N天
            closes_list = list(closes)
            closes_list[-1] = current_price  # 替换最后一天为实时价格
            
            # 计算最近5/10/20天的均价
            if len(closes_list) >= 5:
                live_ma5 = np.mean(closes_list[-5:])
            else:
                live_ma5 = static_ma5
                
            if len(closes_list) >= 10:
                live_ma10 = np.mean(closes_list[-10:])
            else:
                live_ma10 = static_ma10
                
            if len(closes_list) >= 20:
                live_ma20 = np.mean(closes_list[-20:])
            else:
                live_ma20 = static_ma20
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
            height = abs(closes[i] - opens[i])
            if height == 0:
                height = 0.01  # 避免高度为0
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
        
        # 在左上角添加价格信息框（同时显示静态和动态均线）
        if use_realtime:
            info_text = (
                f'{price_label}: {current_price:.2f}\n'
                f'─────────────────\n'
                f'MA5:  {static_ma5:.2f} → {live_ma5:.2f}\n'
                f'MA10: {static_ma10:.2f} → {live_ma10:.2f}\n'
                f'MA20: {static_ma20:.2f} → {live_ma20:.2f}\n'
                f'(Static → Live)'
            )
        else:
            info_text = (
                f'{price_label}: {current_price:.2f}\n'
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
        self.ax.set_xticklabels(x_labels, rotation=45)
        
        # 设置Y轴
        self.ax.set_ylabel('Price (CNY)', fontsize=10)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        
        # 调整布局
        self.figure.tight_layout()
    
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
        """刷新所有股票行情（使用多线程）"""
        if not self.stock_list:
            return
        
        for stock_code in self.stock_list:
            # 如果该股票的线程还在运行，跳过
            if stock_code in self.workers and self.workers[stock_code].isRunning():
                continue
            
            # 创建新的工作线程
            worker = QuoteWorker(stock_code)
            worker.quote_ready.connect(self.on_quote_ready)
            worker.error_occurred.connect(self.on_quote_error)
            worker.finished.connect(lambda code=stock_code: self.on_worker_finished(code))
            
            self.workers[stock_code] = worker
            worker.start()
    
    def on_quote_ready(self, quote):
        """处理获取到的行情数据"""
        stock_code = quote['code']
        self.quote_cache[stock_code] = quote
        
        # 检查是否有错误
        if quote.get('error'):
            self.log_message(f"❌ {stock_code} ({quote.get('name', '未知')}): {quote['error']}")
        else:
            self.log_message(f"✅ {stock_code} ({quote['name']}) 行情更新成功")
        
        # 更新显示
        self.update_display()
    
    def on_quote_error(self, stock_code, error_msg):
        """处理获取行情时的错误"""
        self.log_message(f"❌ 获取 {stock_code} 行情异常: {error_msg}")
    
    def on_worker_finished(self, stock_code):
        """工作线程完成"""
        if stock_code in self.workers:
            worker = self.workers[stock_code]
            # 确保线程完全停止
            if worker.isRunning():
                worker.quit()
                worker.wait(100)
            del self.workers[stock_code]
    
    def update_display(self):
        """更新行情显示"""
        self.stock_table.setRowCount(len(self.stock_list))
        
        for row, stock_code in enumerate(self.stock_list):
            if stock_code in self.quote_cache:
                quote = self.quote_cache[stock_code]
                
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
                
                # 总市值（亿）
                market_cap = quote.get('market_cap', 0)
                if market_cap > 0:
                    market_cap_text = f"{market_cap:.2f}亿"
                else:
                    market_cap_text = "-"
                market_cap_item = QTableWidgetItem(market_cap_text)
                market_cap_item.setTextAlignment(Qt.AlignCenter)
                self.stock_table.setItem(row, 5, market_cap_item)
                
                # 流通值（亿）
                circulation = quote.get('circulation', 0)
                if circulation > 0:
                    circulation_text = f"{circulation:.2f}亿"
                else:
                    circulation_text = "-"
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
    
    def create_chart_widget(self):
        """创建K线图显示区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        label = QLabel("📊 K-Line Chart")
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        label.setFixedHeight(40)
        layout.addWidget(label)
        
        # K线图内容区域
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
        from matplotlib.figure import Figure
        
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # 添加工具栏（支持缩放、平移等）
        self.toolbar = NavigationToolbar(self.canvas, widget)
        layout.addWidget(self.toolbar)
        
        # 初始化空图表
        self.ax.text(0.5, 0.5, 'Click stock to view K-Line chart', 
                    ha='center', va='center', fontsize=12)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        layout.addWidget(self.canvas)
        
        return widget
    
    def create_chat_widget(self):
        """创建大模型对话区域（暂时隐藏）"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("🤖 AI 智能助手")
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(label)
        
        # 对话内容区域
        content = QTextEdit()
        content.setPlaceholderText("与 AI 助手对话...")
        layout.addWidget(content)
        
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
        
        label = QLabel("💰 交易操作")
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(label)
        
        # 交易内容区域
        content = QTextEdit()
        content.setPlaceholderText("交易操作界面...")
        layout.addWidget(content)
        
        return widget


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = TradingPanel()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
