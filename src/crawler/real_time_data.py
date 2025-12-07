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
            "Cookie": "xq_a_token=9492bad942dadf90b60f270aac7d5b5e982fdf82; xqat=9492bad942dadf90b60f270aac7d5b5e982fdf82; xq_r_token=edf6f46eaceb40d684979451929ef3d7c0928034; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTc2Njc5ODE1MSwiY3RtIjoxNzY0ODQyNjU3NzY5LCJjaWQiOiJkOWQwbjRBWnVwIn0.iYRTiPGm73jTMkeJNdksIHrxMdTj4ETP81IA2dF80nodjTumV8WXO4D99pkXNyOOGzw9XTLT6LS5BvfSwo16R4INPlJZJXJnQ7tughLcRxPK-0FoaCL6ZHQYFpi10xdbpSJRl3PMZKUBfl87BzYyD7oGvrEewY3aY1d_qEv4xOHEj70wqecpUfw7jwItjb4o8RVoh7R9ZAgnALRfwcG7yGeH2jTbN0RVUvHsgEeSde1fPd2zWnKR9vGeUfn_xBs-dCYpD6yXwBQBuBcjd67iIquAYjsRcCY2NbjRhDut80N8xG5xwEgN7OX1amGEx_3vozWeO4O_75W3zXNeQDQ1Bw; cookiesu=931764842715080; u=931764842715080; device_id=26e0857e322721bc0304e452a0807a35; Hm_lvt_1db88642e346389874251b5a1eded6e3=1764842720; HMACCOUNT=38D66FD954EA0CCF; s=a511lm96bq; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1764843385; is_overseas=0; ssxmod_itna=1-CqGxuQG=KYqWwxeKYKitriODCDm2D_pGaxBP017sDu2xjKidQDU7YNg0rtEDiTPue=8Ci7GqbqnxGXkmDA5Dnzx7YDtrSPN=enpAGwkT7R7ipoS/rGoh63L7iwk63aL94qMj6vz1qSnoh5bDB3DbqDy8Ge=YxGGf4GwDGoD34DiDDpfD03Db4D_SjrD72btxaWdheqDQ4GyDitDKqqaxG3D0RRobGAQoDDlY774IGauDYPdVji72iFDAuGNv74dx0taDBd5nIDdxDU6MIGbVCSfrFoY1caDtqD9f6uqpaIQN=nKrIeKBroVr4U0DKgDI7GGWxzCGeYYdBG3WheBX3mm5GDeA0xBixfwt4DASYHB4NBPo7yMmvpAvZFeFeT1/qHDTrK9DIDHtut8BN4_K8YeYxepYNK0q7i5OiPeD; ssxmod_itna2=1-CqGxuQG=KYqWwxeKYKitriODCDm2D_pGaxBP017sDu2xjKidQDU7YNg0rtEDiTPue=8Ci7GqbqYxD3beYcloWvtvALyXG8b0q_WXeeD",
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