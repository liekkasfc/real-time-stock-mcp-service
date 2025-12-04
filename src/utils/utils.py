"""
通用工具函数
"""

import logging
import sys
from datetime import datetime, timedelta
from typing import Optional


def setup_logging(level=logging.INFO):
    """
    配置日志系统
    
    Args:
        level: 日志级别
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )


def format_date(date_obj: datetime) -> str:
    """
    将datetime对象格式化为YYYY-MM-DD字符串
    
    Args:
        date_obj: datetime对象
        
    Returns:
        格式化的日期字符串
    """
    return date_obj.strftime('%Y-%m-%d')


def parse_date(date_str: str) -> Optional[datetime]:
    """
    解析日期字符串为datetime对象
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        
    Returns:
        datetime对象，解析失败返回None
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None


def get_date_range(days: int = 30) -> tuple[str, str]:
    """
    获取从今天往前指定天数的日期范围
    
    Args:
        days: 天数
        
    Returns:
        (start_date, end_date) 元组
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return format_date(start_date), format_date(end_date)


def format_number(num: float, decimal_places: int = 2) -> str:
    """
    格式化数字，添加千位分隔符
    
    Args:
        num: 数字
        decimal_places: 小数位数
        
    Returns:
        格式化后的字符串
    """
    if num is None:
        return 'N/A'
    return f'{num:,.{decimal_places}f}'


def format_percentage(num: float, decimal_places: int = 2) -> str:
    """
    格式化百分比
    
    Args:
        num: 数字（如 0.05 表示 5%）
        decimal_places: 小数位数
        
    Returns:
        格式化后的百分比字符串
    """
    if num is None:
        return 'N/A'
    return f'{num * 100:.{decimal_places}f}%'


def safe_float(value, default=0.0) -> float:
    """
    安全地将值转换为浮点数
    
    Args:
        value: 待转换的值
        default: 默认值
        
    Returns:
        浮点数
    """
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0) -> int:
    """
    安全地将值转换为整数
    
    Args:
        value: 待转换的值
        default: 默认值
        
    Returns:
        整数
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    截断字符串
    
    Args:
        text: 原始字符串
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的字符串
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
