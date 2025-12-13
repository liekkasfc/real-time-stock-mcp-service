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

    @app.tool()
    def get_smart_score_rank(stock_code: str) -> str:
        """
        获取个股智能评分排名数据
        """
        try:
            # 调用数据源获取智能评分排名数据
            rank_data = data_source.get_smart_score_rank(stock_code)
            
            if not rank_data:
                return "未找到相关评分排名数据"

            # 格式化为Markdown表格
            result = f"**个股智能评分排名详情**\n\n"
            result += f"股票代码：{rank_data.get('SECUCODE', stock_code)}\n"
            result += f"股票名称：{rank_data.get('SECURITY_NAME_ABBR', '')}\n"
            result += f"所属板块：{rank_data.get('BOARD_NAME', '')}({rank_data.get('BOARD_CODE', '')})\n\n"
            result += f"交易日期：{rank_data.get('TRADE_DATE', '').split(' ')[0]}\n"
            
            # 综合评分部分
            result += f"**综合评分**\n"
            result += f"综合评分：{rank_data.get('COMPRE_SCORE', 0):.2f}分\n"
            result += f"当日涨跌幅：{rank_data.get('CHANGE_RATE', 0):+.2f}%\n\n"
            
            # 行业内排名部分
            result += f"**行业内排名**\n"
            result += f"行业排名：第{rank_data.get('INDUSTRY_RANK', 0)}名\n"
            result += f"行业最高分：{rank_data.get('INDUSTRY_SCORE_HIGH', 0):.2f}分\n"
            result += f"行业平均分：{rank_data.get('INDUSTRY_SCORE_AVG', 0):.2f}分\n"
            result += f"行业最低分：{rank_data.get('INDUSTRY_SCORE_LOW', 0):.2f}分\n"
            result += f"{rank_data.get('BOARD_NAME', '')}行业共{rank_data.get('INDUSTRY_STOCK_NUM', 0)}只股票，已评{rank_data.get('EVALUATE_INDUSTRY_NUM', 0)}只\n\n"
            
            # 全市场排名部分
            result += f"**全市场排名**\n"
            result += f"市场排名：第{rank_data.get('MARKET_RANK', 0)}名\n"
            result += f"打败了市场{rank_data.get('STOCK_RANK_RATIO', 0):.2f}%的股票\n"
            result += f"市场最高分：{rank_data.get('MARKET_SCORE_HIGH', 0):.2f}分\n"
            result += f"市场平均分：{rank_data.get('MARKET_SCORE_AVG', 0):.2f}分\n"
            result += f"市场最低分：{rank_data.get('MARKET_SCORE_LOW', 0):.2f}分\n"
            result += f"沪深市场共{rank_data.get('MARKET_STOCK_NUM', 0)}只股票，已评{rank_data.get('EVALUATE_MARKET_NUM', 0)}只"
            
            return result
        except Exception as e:
            logger.error(f"获取个股智能评分排名数据失败: {e}")
            return f"获取个股智能评分排名数据失败: {e}"