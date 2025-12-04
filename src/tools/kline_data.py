"""
K线数据工具

提供K线数据查询和分析功能
"""
import logging
from mcp.server.fastmcp import FastMCP
from ..data_source_interface import FinancialDataInterface
from ..utils import format_number, format_percentage

logger = logging.getLogger(__name__)


def register_kline_tools(app: FastMCP, data_source: FinancialDataInterface):
    """
    注册K线数据相关工具

    Args:
        app: FastMCP应用实例
        data_source: 数据源实例
    """

    @app.tool()
    def get_kline(
        stock_code: str,
        start_date: str,
        end_date: str,
        frequency: str = "d"
    ) -> str:
        """
        获取K线数据

        获取指定股票在指定日期范围内的K线数据。

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD格式)
            end_date: 结束日期 (YYYY-MM-DD格式)
            frequency: K线周期，可选值: "d"(日), "w"(周), "m"(月), "5"(5分钟), "15"(15分钟), "30"(30分钟), "60"(60分钟)

        Returns:
            K线数据的Markdown表格

        Examples:
            - get_kline("600519", "2024-01-01", "2024-01-31")
            - get_kline("000001", "2024-10-01", "2024-10-31", "w")
        """
        try:
            logger.info(f"获取K线: {stock_code}, {start_date} 至 {end_date}, 频率: {frequency}")
            kline_data = data_source.get_historical_k_data(stock_code, start_date, end_date, frequency)

            if not kline_data:
                return f"未找到股票代码 '{stock_code}' 在 {start_date} 至 {end_date} 的K线数据"

            # 格式化数据
            formatted_data = []
            for k in kline_data:
                open_price = k.get('open', 0)  # 开盘价
                close_price = k.get('close', 0)  # 收盘价
                high_price = k.get('high', 0)  # 最高价
                low_price = k.get('low', 0)  # 最低价
                volume = k.get('volume', 0)  # 成交量
                amount = k.get('amount', 0)  # 成交额
                change_pct = k.get('change_percent', 0)  # 涨跌幅(%)
                amplitude = k.get('amplitude', 0)  # 振幅(%)
                change_amount = k.get('change_amount', 0)  # 涨跌额
                turnover_rate = k.get('turnover_rate', 0)  # 换手率(%)

                # ------------------------------
                # 计算 K 线状态（阳线/阴线/十字星）
                # ------------------------------
                if close_price > open_price:
                    status = "上涨（阳线）"
                elif close_price < open_price:
                    status = "下跌（阴线）"
                else:
                    status = "平盘（十字星）"

                # ------------------------------
                # 格式化输出
                # ------------------------------
                formatted_data.append({
                    '日期': k.get('date', ''),
                    'K线状态': status,
                    '开盘': format_number(open_price),
                    '收盘': format_number(close_price),
                    '最高': format_number(high_price),
                    '最低': format_number(low_price),
                    '涨跌幅': f"{'+' if change_pct > 0 else ''}{change_pct:.2f}%",
                    '成交量': format_number(volume, 0),
                    '成交额': format_number(amount, 0),
                    '振幅': f"{amplitude:.2f}%",
                    '涨跌额': format_number(change_amount),
                    '换手率': f"{turnover_rate:.2f}%"
                })

            # 手动构建Markdown表格
            columns = ['日期', 'K线状态', '开盘', '收盘', '最高', '最低', '涨跌幅', '成交量', '成交额', '振幅', '涨跌额', '换手率']

            # 创建表头
            header = "| " + " | ".join(columns) + " |"
            separator = "| " + " | ".join(["---"] * len(columns)) + " |"

            # 创建数据行
            rows = []
            for item in formatted_data:
                row_data = [str(item.get(col, "")) for col in columns]
                row = "| " + " | ".join(row_data) + " |"
                rows.append(row)

            # 组合表格
            table = "\n".join([header, separator] + rows)

            note = f"\n\n💡 显示 {len(formatted_data)} 条K线数据，频率: {frequency}"
            return f"## {stock_code} K线数据\n\n{table}{note}"

        except Exception as e:
            logger.error(f"获取K线时出错: {e}")
            return f"获取K线失败: {str(e)}"

    @app.tool()
    def get_technical_indicators(
        stock_code: str,
        start_date: str,
        end_date: str,
        frequency: str = "d"
    ) -> str:
        """
        获取技术指标数据

        获取指定股票在指定日期范围内的技术指标数据。
        注: 日期范围会限制计算长期数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD格式)
            end_date: 结束日期 (YYYY-MM-DD格式)
            frequency: K线周期，可选值: "d"(日), "w"(周), "m"(月), "5"(5分钟), "15"(15分钟), "30"(30分钟), "60"(60分钟)

        Returns:
            技术指标数据的Markdown表格

        Examples:
            - get_technical_indicators("600519", "2024-01-01", "2024-01-31")
            - get_technical_indicators("000001", "2024-10-01", "2024-10-31", "w")
        """
        try:
            logger.info(f"获取技术指标: {stock_code}, {start_date} 至 {end_date}, 频率: {frequency}")
            indicator_data = data_source.get_technical_indicators(stock_code, start_date, end_date, frequency)

            if not indicator_data:
                return f"未找到股票代码 '{stock_code}' 在 {start_date} 至 {end_date} 的技术指标数据"

            # 格式化数据
            formatted_data = []
            for item in indicator_data:
                formatted_data.append({
                    '日期': item.get('date', ''),
                    'MA5': format_number(item.get('ma5', 0)),
                    'MA10': format_number(item.get('ma10', 0)),
                    'MA20': format_number(item.get('ma20', 0)),
                    'MA60': format_number(item.get('ma60', 0)),
                    'DIF': format_number(item.get('macd_dif', 0)),
                    'DEA': format_number(item.get('macd_dea', 0)),
                    'MACD柱': format_number(item.get('macd_bar', 0)),
                    'RSI6': format_number(item.get('rsi6', 0)),
                    'RSI12': format_number(item.get('rsi12', 0)),
                    'RSI24': format_number(item.get('rsi24', 0)),
                    'KDJ_K': format_number(item.get('kdj_k', 0)),
                    'KDJ_D': format_number(item.get('kdj_d', 0)),
                    'KDJ_J': format_number(item.get('kdj_j', 0))
                })

            # 手动构建Markdown表格
            columns = ['日期', 'MA5', 'MA10', 'MA20', 'MA60', 'DIF', 'DEA', 'MACD柱', 'RSI6', 'RSI12', 'RSI24', 'KDJ_K', 'KDJ_D', 'KDJ_J']

            # 创建表头
            header = "| " + " | ".join(columns) + " |"
            separator = "| " + " | ".join(["---"] * len(columns)) + " |"

            # 创建数据行
            rows = []
            for item in formatted_data:
                row_data = [str(item.get(col, "")) for col in columns]
                row = "| " + " | ".join(row_data) + " |"
                rows.append(row)

            # 组合表格
            table = "\n".join([header, separator] + rows)

            note = f"\n\n💡 显示 {len(formatted_data)} 条技术指标数据，频率: {frequency}"
            return f"## {stock_code} 技术指标数据\n\n{table}{note}"

        except Exception as e:
            logger.error(f"获取技术指标时出错: {e}")
            return f"获取技术指标失败: {str(e)}"