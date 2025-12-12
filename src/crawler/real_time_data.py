import requests
from typing import Dict, Any, Optional
from .base_crawler import EastMoneyBaseSpider


class RealTimeDataSpider(EastMoneyBaseSpider):
    """
    雪球实时股票数据爬虫

    用于获取股票的实时行情数据
    """

    BASE_URL = "https://stock.xueqiu.com/v5/stock/quote.json"

    def __init__(
            self,
            session: Optional[requests.Session] = None,
            timeout: int = None,
    ):
        super().__init__(session, timeout)
        # 设置雪球网站需要的特定headers
        self.headers.update({
            "Referer": "https://xueqiu.com/",
            "Host": "stock.xueqiu.com",
            "Cookie": "cookiesu=931764842715080; device_id=26e0857e322721bc0304e452a0807a35; Hm_lvt_1db88642e346389874251b5a1eded6e3=1764842720; s=a511lm96bq; xq_a_token=7ed879d430984f6ea5a546808b7b9fcd64f39eb9; xqat=7ed879d430984f6ea5a546808b7b9fcd64f39eb9; xq_r_token=ef2ca2a5140cc8bab4810c2509fdec718b6f63a5; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTc2ODA5NDE1NSwiY3RtIjoxNzY1NTMyMzYyNTIyLCJjaWQiOiJkOWQwbjRBWnVwIn0.p9RgDKoZfPSguPKihs84JLR3UqnNBElDgNVX81xvQY42K6Z7MGwV85DSB66c2z7HeZeKeYdHz3sM9KLLUOOPVUP0IliP-Y5B9X0L5YZrOn-rU7vw2NS7Hhe46hs-p81Ll7q1gMuaMoPER71_MX9IPUViDSzoJHPMlg312xA1avbDU46KQORokqwuOIrKr_8Mgr_YDny3XQINVe4ODwVV6Z_hYrxZ1P7sbIige0MuCbntbz6YfzE-QcVVbRqTUV2v6h22-oJbooGlAHQX6pPp6J8AZIOy_zD6JPGrLvcK1QMiRyF_sh7ZDgzu7PnPanjWu2xTUVO99cTzrR9AZoBE0Q; u=931764842715080",
        })

    def _add_exchange_prefix(self, symbol: str) -> str:
        """
        为A股股票代码自动添加交易所前缀
        
        :param symbol: 股票代码，可能是纯数字或已经带有前缀
        :return: 带有交易所前缀的股票代码
        """
        # 如果已经是带前缀的格式，则直接返回
        if symbol.startswith(("SH", "SZ")):
            return symbol
            
        # 如果是纯数字代码，则根据规则添加前缀
        if symbol.isdigit():
            # 5位数字是港股，不添加前缀
            if len(symbol) == 5:
                return symbol
            # 上交所股票代码以6开头
            elif symbol.startswith('6'):
                return f"SH{symbol}"
            # 深交所股票代码以0、3开头
            elif symbol.startswith(('0', '3')):
                return f"SZ{symbol}"
        # 其他情况
        return symbol

    def get_real_time_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票实时数据

        :param symbol: 股票代码，支持纯数字代码（A股），也支持带交易所代码的格式，如 SZ300750 或 SH600519，港股无需前缀
        :return: 实时股票数据
        """
        # 自动添加交易所前缀（仅适用于A股）
        formatted_symbol = self._add_exchange_prefix(symbol)
        
        params = {
            "symbol": formatted_symbol,
            "extend": "detail"
        }

        response = self._get_json(self.BASE_URL, params)
        # 检查是否有错误码，如果有错误则抛出异常
        error_code = response.get("error_code", 0)
        error_description = response.get("error_description", "")

        if error_code != 0:
            raise Exception(f"获取数据失败: {error_code} - {error_description}")

        # 根据要求返回"data"部分
        return response.get("data", {})


if __name__ == '__main__':
    # 创建爬虫实例
    spider = RealTimeDataSpider()
    # 获取宁德时代的实时数据
    data = spider.get_real_time_data("SZ300750")
    print(data)