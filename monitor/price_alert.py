#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
价格预警模块 - 监控股票触及均线等条件
"""

from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal


class PriceAlert(QObject):
    """价格预警器"""
    
    # 预警信号
    alert_triggered = pyqtSignal(str, str, dict)  # (stock_code, alert_type, data)
    
    def __init__(self):
        super().__init__()
        self.alert_rules = {}  # 预警规则
        self.alert_history = {}  # 预警历史（防止重复预警）
        
    def add_rule(self, stock_code, rule_type, params):
        """
        添加预警规则
        
        Args:
            stock_code: 股票代码
            rule_type: 规则类型 (ma5_cross, ma10_cross, price_break, etc.)
            params: 规则参数
        """
        if stock_code not in self.alert_rules:
            self.alert_rules[stock_code] = []
        
        self.alert_rules[stock_code].append({
            'type': rule_type,
            'params': params,
            'enabled': True
        })
    
    def remove_rule(self, stock_code, rule_type=None):
        """删除预警规则"""
        if rule_type is None:
            # 删除该股票所有规则
            if stock_code in self.alert_rules:
                del self.alert_rules[stock_code]
        else:
            # 删除特定类型规则
            if stock_code in self.alert_rules:
                self.alert_rules[stock_code] = [
                    r for r in self.alert_rules[stock_code] 
                    if r['type'] != rule_type
                ]
    
    def check_alerts(self, stock_code, quote_data, kline_data=None):
        """
        检查预警条件
        
        Args:
            stock_code: 股票代码
            quote_data: 实时行情数据
            kline_data: K线数据（包含均线）
        """
        if stock_code not in self.alert_rules:
            return
        
        current_price = quote_data.get('price', 0)
        if current_price <= 0:
            return
        
        for rule in self.alert_rules[stock_code]:
            if not rule['enabled']:
                continue
            
            rule_type = rule['type']
            params = rule['params']
            
            # 检查不同类型的预警
            if rule_type == 'ma5_touch' and kline_data is not None:
                self._check_ma_touch(stock_code, current_price, kline_data, 'ma5', params)
            
            elif rule_type == 'ma10_touch' and kline_data is not None:
                self._check_ma_touch(stock_code, current_price, kline_data, 'ma10', params)
            
            elif rule_type == 'ma20_touch' and kline_data is not None:
                self._check_ma_touch(stock_code, current_price, kline_data, 'ma20', params)
            
            elif rule_type == 'price_break':
                self._check_price_break(stock_code, current_price, params)
            
            elif rule_type == 'change_pct':
                self._check_change_pct(stock_code, quote_data, params)
    
    def _check_ma_touch(self, stock_code, current_price, kline_data, ma_type, params):
        """检查是否触及均线"""
        if ma_type not in kline_data.columns:
            return
        
        ma_value = kline_data[ma_type].dropna().iloc[-1] if not kline_data[ma_type].dropna().empty else 0
        if ma_value <= 0:
            return
        
        # 计算价格与均线的偏离度
        deviation = abs(current_price - ma_value) / ma_value * 100
        threshold = params.get('threshold', 0.5)  # 默认0.5%以内算触及
        
        # 检查是否触及
        if deviation <= threshold:
            alert_key = f"{stock_code}_{ma_type}_touch"
            
            # 防止重复预警（5分钟内不重复）
            if self._should_alert(alert_key):
                self.alert_triggered.emit(
                    stock_code,
                    f'触及{ma_type.upper()}',
                    {
                        'current_price': current_price,
                        'ma_value': ma_value,
                        'deviation': deviation,
                        'direction': 'above' if current_price > ma_value else 'below'
                    }
                )
    
    def _check_price_break(self, stock_code, current_price, params):
        """检查价格突破"""
        target_price = params.get('target_price', 0)
        direction = params.get('direction', 'above')  # above/below
        
        if direction == 'above' and current_price >= target_price:
            alert_key = f"{stock_code}_break_above_{target_price}"
            if self._should_alert(alert_key):
                self.alert_triggered.emit(
                    stock_code,
                    '价格突破',
                    {
                        'current_price': current_price,
                        'target_price': target_price,
                        'direction': 'above'
                    }
                )
        
        elif direction == 'below' and current_price <= target_price:
            alert_key = f"{stock_code}_break_below_{target_price}"
            if self._should_alert(alert_key):
                self.alert_triggered.emit(
                    stock_code,
                    '价格突破',
                    {
                        'current_price': current_price,
                        'target_price': target_price,
                        'direction': 'below'
                    }
                )
    
    def _check_change_pct(self, stock_code, quote_data, params):
        """检查涨跌幅"""
        change_pct = quote_data.get('change_pct', 0)
        threshold = params.get('threshold', 5)  # 默认5%
        
        if abs(change_pct) >= threshold:
            alert_key = f"{stock_code}_change_{int(change_pct)}"
            if self._should_alert(alert_key):
                self.alert_triggered.emit(
                    stock_code,
                    '涨跌幅预警',
                    {
                        'change_pct': change_pct,
                        'threshold': threshold
                    }
                )
    
    def _should_alert(self, alert_key):
        """判断是否应该发出预警（防止重复）"""
        now = datetime.now()
        
        if alert_key in self.alert_history:
            last_alert_time = self.alert_history[alert_key]
            # 5分钟内不重复预警
            if (now - last_alert_time).total_seconds() < 300:
                return False
        
        self.alert_history[alert_key] = now
        return True
    
    def clear_history(self):
        """清空预警历史"""
        self.alert_history.clear()
