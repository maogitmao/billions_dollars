#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
事件总线 - 模块间解耦通信
"""

from typing import Callable, Dict, List, Any
from collections import defaultdict
import threading


class EventBus:
    """
    事件总线（单例模式）
    用于模块间的解耦通信
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
        self._initialized = True
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        with self._lock:
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """
        取消订阅
        
        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        with self._lock:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
    
    def publish(self, event_type: str, data: Any = None):
        """
        发布事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        with self._lock:
            callbacks = self._subscribers[event_type].copy()
        
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"事件处理错误 [{event_type}]: {e}")
    
    def clear(self, event_type: str = None):
        """
        清除订阅
        
        Args:
            event_type: 事件类型，None表示清除所有
        """
        with self._lock:
            if event_type:
                self._subscribers[event_type].clear()
            else:
                self._subscribers.clear()


# 事件类型常量
class EventType:
    """事件类型定义"""
    
    # 数据事件
    DATA_UPDATED = 'data_updated'              # 数据更新
    QUOTE_UPDATED = 'quote_updated'            # 行情更新
    KLINE_UPDATED = 'kline_updated'            # K线更新
    INDICATOR_UPDATED = 'indicator_updated'    # 指标更新
    
    # 信号事件
    SIGNAL_GENERATED = 'signal_generated'      # 信号产生
    BUY_SIGNAL = 'buy_signal'                  # 买入信号
    SELL_SIGNAL = 'sell_signal'                # 卖出信号
    
    # 预警事件
    ALERT_TRIGGERED = 'alert_triggered'        # 预警触发
    PRICE_ALERT = 'price_alert'                # 价格预警
    VOLUME_ALERT = 'volume_alert'              # 成交量预警
    
    # 交易事件
    ORDER_CREATED = 'order_created'            # 订单创建
    ORDER_EXECUTED = 'order_executed'          # 订单执行
    ORDER_CANCELLED = 'order_cancelled'        # 订单取消
    
    # 策略事件
    STRATEGY_CHANGED = 'strategy_changed'      # 策略变更
    STRATEGY_STARTED = 'strategy_started'      # 策略启动
    STRATEGY_STOPPED = 'strategy_stopped'      # 策略停止
    
    # 系统事件
    SYSTEM_ERROR = 'system_error'              # 系统错误
    LOG_MESSAGE = 'log_message'                # 日志消息
    
    # AI事件
    AI_ANALYSIS_READY = 'ai_analysis_ready'    # AI分析完成
    AI_PREDICTION_READY = 'ai_prediction_ready' # AI预测完成


# 全局事件总线实例
event_bus = EventBus()
