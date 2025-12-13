"""
智能点评MCP工具
src/mcp_tools/smart_review.py
提供股票智能点评相关的MCP工具
"""

import logging
from mcp.server.fastmcp import FastMCP

from src.data_source_interface import FinancialDataInterface
from src.utils.markdown_formatter import format_list_to_markdown_table

logger = logging.getLogger(__name__)


def register_smart_review_tools(app: FastMCP, data_source: FinancialDataInterface):
    """
    注册智能点评相关工具
    
    Args:
        server: MCP服务器实例
        data_source: 数据源实例
    """
    @app.tool()
    def get_smart_score(stock_code: str) -> str:
        """
        获取股票智能评分数据
        """
        try:
            # 调用数据源获取智能评分数据
            score_data = data_source.get_smart_score(stock_code)


            # 直接格式化为逐行显示
            result = f"**股票智能评分**\n\n"
            result += f"股票代码：{score_data.get('SECUCODE', stock_code)}\n"
            result += f"股票名称：{score_data.get('SECURITY_NAME_ABBR', stock_code)}\n"
            result += f"评分：{score_data.get('TOTAL_SCORE', 0):.2f}\n"
            result += f"评分变化：{score_data.get('TOTAL_SCORE_CHANGE', 0):+.2f}\n"
            result += f"次日上涨概率：{score_data.get('RISE_1_PROBABILITY', 0):.2f}%\n"
            result += f"次日平均涨跌：{score_data.get('AVERAGE_1_INCREASE', 0):.2f}%\n"
            result += f"五日上涨概率：{score_data.get('RISE_5_PROBABILITY', 0):.2f}%\n"
            result += f"五日平均涨跌：{score_data.get('AVERAGE_5_INCREASE', 0):.2f}%\n"
            result += f"分析解读：{score_data.get('WORDS_EXPLAIN', '')}\n"
            result += f"分析时间：{score_data.get('DIAGNOSE_TIME', '')}"
            
            return result
        except Exception as e:
            logger.error(f"获取股票智能评分数据失败: {e}")
            return f"获取股票智能评分数据失败 {e}"