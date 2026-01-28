#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志工具
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from config import LOG_LEVEL, LOG_FILE, LOG_MAX_SIZE, LOG_BACKUP_COUNT


def get_logger(name: str = 'billions_dollars') -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        Logger实例
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # 格式化
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件输出（带轮转）
    try:
        log_path = Path(LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"无法创建日志文件: {e}")
    
    return logger
