import requests
from typing import List, Optional, Dict
import random

class EastMoneyKlineSpider:
    """
    东方财富 K 线数据爬虫封装类
    主要功能：根据股票代码、日期区间、周期、复权方式，获取历史 K 线数据（klines 字段）
    """

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        """
        初始化方法：
        - 可以传入一个已有的 requests.Session（方便复用连接、挂代理等）
        - 如果不传，则内部自己创建一个 Session
        """
        self.session = session or requests.Session()

        # 东方财富历史 K 线接口基础地址
        self.base_url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"

        # 通用请求头：模拟浏览器，避免被简单风控拦截
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7",
            "Connection": "keep-alive",
            "Referer": "https://quote.eastmoney.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/142.0.0.0 Safari/537.36"
            ),
        }

        # cookies：从浏览器复制的一份，可选（很多时候不写也能正常返回）
        # 如果你发现某天突然不能用了，可以尝试更新这一份 cookies
        self.cookies = {
            "qgqp_b_id": "0fcbf3bdb1b2f66e82ab5798a1b81b4d",
            "st_nvi": "qGQQJbcyOYbgD3P3VjxZq3b76",
            "fullscreengg": "1",
            "fullscreengg2": "1",
            "st_si": "89872530764969",
            "nid18": "0e91efe5fbd6fc173b78a19a83d0af1d",
            "nid18_create_time": "1764333371304",
            "gviem": "Ng6cf2ZLz0ADMZDiSt9Cs0a99",
            "gviem_create_time": "1764333371304",
            "wsc_checkuser_ok": "1",
            "websitepoptg_api_time": "1764399842308",
            "st_asi": "delete",
            "st_pvi": "46742110456760",
            "st_sp": "2025-09-15%2022%3A42%3A47",
            "st_inirUrl": "https%3A%2F%2Fcn.bing.com%2F",
            "st_sn": "53",
            "st_psi": "20251129192501864-113200301201-6489312293",
        }

    # ===================== 内部工具方法 =====================

    def _format_secid(self, stock_codes: str) -> str:
        """
        将各种常见格式的股票代码，转换成东方财富接口需要的 secid 格式：
        - 格式为：{market}.{code}
        - market: 0 = 深市(SZ)，1 = 沪市(SH)

        支持的输入格式示例：
        - "000977"        -> 默认为深市：0.000977
        - "600000"        -> 以 6 开头，默认沪市：1.600000
        - "000977.SZ"     -> 按后缀 SZ / SH 判断
        - "600000.SH"     -> 按后缀 SZ / SH 判断
        - "0.000977" / "1.600000" -> 认为已经是 secid，直接返回

        :param stock_codes: 股票代码字符串
        :return: 形如 "0.000977" 的 secid 字符串
        """
        code = stock_codes.strip()

        # 1. 如果已经是类似 "0.000977" 这种形式，直接返回
        if "." in code:
            left, right = code.split(".", maxsplit=1)

            # 如果 left 是 "0"/"1"，right 是纯数字，认为本身就是 secid
            if left in {"0", "1"} and right.isdigit():
                return code

            # 如果是 "000977.SZ" 这一类
            market_suffix = right.upper()
            if market_suffix in {"SZ", "SH"}:
                # SZ -> 0, SH -> 1
                market = "0" if market_suffix == "SZ" else "1"
                return f"{market}.{left}"

        # 2. 只给了纯数字代码，例如 "000977" 或 "600000"
        if code.isdigit():
            # 以 6 开头的通常是沪市，其它默认深市（简单规则，够用）
            if code.startswith("6"):
                market = "1"  # 沪市
            else:
                market = "0"  # 深市
            return f"{market}.{code}"

        # 3. 兜底：如果传进来的格式很奇怪，直接抛异常提醒
        raise ValueError(f"无法解析股票代码格式: {stock_codes}")

    # ===================== 对外核心方法 =====================

    def get_k_history_data(
        self,
        stock_codes: str,              # 股票代码
        beg: str = "19000101",         # 开始日期，格式：YYYYMMDD
        end: str = "20500101",         # 结束日期，格式：YYYYMMDD
        klt: int = 101,                # 周期：1/5/15/30/60 分钟；101 日；102 周；103 月
        fqt: int = 1,                  # 复权方式：0 不复权 1 前复权 2 后复权
        timeout: int = 20,             # 请求超时时间（秒）
    ) -> List[str]:
        """
        获取指定股票的历史 K 线数据（返回原始 klines 列表）。

        :param stock_codes: 股票代码（支持 "000977" / "000977.SZ" / "0.000977" 等多种格式）
        :param beg: 开始日期，形如 "19000101"
        :param end: 结束日期，形如 "20500101"
        :param klt: 行情之间的时间间隔
        :param fqt: 复权方式
        :param timeout: 请求超时时间（秒）
        :return: 东方财富接口返回的 "klines" 列表
        """
        # 1. 将股票代码格式转换为 secid
        secid = self._format_secid(stock_codes)

        # 2. 组装请求参数
        params = {
            # 第一组字段（固定写法，基本不用改）
            "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
            # 第二组字段（包含时间、开高低收、成交量等）
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "beg": beg,
            "end": end,
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "rtntype": "6",
            "secid": secid,
            "klt": str(klt),
            "fqt": str(fqt),
        }

        # 3. 发起 GET 请求
        resp = self.session.get(
            self.base_url,
            headers=self.headers,
            cookies=self.cookies,
            params=params,
            timeout=timeout,
        )

        # 如果 HTTP 状态码不是 200，直接抛异常，方便排查
        resp.raise_for_status()

        # 4. 解析 JSON 数据
        data = resp.json()

        # 安全获取 data -> klines，如果没有则抛异常
        if "data" not in data or not data["data"]:
            raise RuntimeError(f"响应中不存在 data 字段，原始响应: {data}")

        k_data = data["data"]
        if "klines" not in k_data:
            raise RuntimeError(f"响应中不存在 klines 字段，原始响应: {data}")

        klines = k_data["klines"]

        # 此处 klines 通常是 List[str]，每个元素类似：
        # "2024-11-29,收盘价,开盘价,最高价,最低价,成交量,成交额,振幅,涨跌额,涨跌幅,换手率"
        return klines


class StockSearcher:
    """
    基于上交所接口的股票查询类

    使用方式：
        searcher = StockSearcher()
        result = searcher.search("宁德")   # 或 "300750"
    """

    # 上交所提供的查询接口基础 URL
    BASE_URL = "https://www.sse.org.cn/api/report/shortname/gethangqing"

    def __init__(self, timeout: int = 10):
        """
        :param timeout: HTTP 请求超时时间（秒）
        """
        self.timeout = timeout
        # 复用 Session，可以减少 TCP 连接开销
        self.session = requests.Session()
        # 默认请求头，伪装成浏览器，避免被误判为爬虫
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/129.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.sse.org.cn/"
        }

    def search(self, keyword: str) -> Optional[List[Dict]]:
        """
        根据关键字（股票代码 / 中文名称 / 模糊汉字）查询股票

        :param keyword: 用户输入，如 "宁德" 或 "宁德时代" 或 "300750"
        :return:
            - 成功：返回一个列表，每个元素为字典
              形如：{"code": "300750", "name": "宁德时代", "pinyinString": "ndsd", ...}
            - 失败（网络错误 / 无数据）：返回 None
        """
        # 构造 URL 参数
        params = {
            # dataType 按你找到的链接保持 [agzqdm]
            "dataType": "[agzqdm]",
            # input 支持中文模糊 和 代码
            "input": keyword,
            # random 可以随便给一个 0~1 的随机数，防止缓存
            "random": str(random.random())
        }

        try:
            # 发送 GET 请求
            resp = self.session.get(
                self.BASE_URL,
                params=params,
                headers=self.headers,
                timeout=self.timeout,
            )
            # 如果状态码不是 200，抛出异常
            resp.raise_for_status()

            # 解析 JSON
            data = resp.json()

        except requests.RequestException as e:
            # 网络相关错误（超时、DNS、连接失败等）
            print(f"[StockSearcher] 请求接口出错: {e}")
            return None
        except ValueError as e:
            # JSON 解析失败
            print(f"[StockSearcher] 解析 JSON 出错: {e}")
            return None

        # 按你提供的返回格式：{"data":[{...}, {...}]}
        items = data.get("data")
        if not items:
            # 没有匹配结果
            print(f"[StockSearcher] 没有找到与 '{keyword}' 匹配的股票")
            return None

        # 这里直接返回原始列表，每个元素是一个 dict
        # 调用方可自行选择第一条 / 精确匹配等策略
        return items


# ===================== 使用示例 =====================
if __name__ == "__main__":
    spider = EastMoneyKlineSpider()

    # 示例：000977 深市股票，获取全部日 K 前复权
    kl = spider.get_k_history_data(
        stock_codes="300750",   # 你也可以写 "000977.SZ" 或 "0.000977"
        beg="20251123",  # 表示 2025年1月1日
        end="20251128",
        klt=101,               # 日 K
        fqt=1,                 # 前复权
    )

    print(f"共获取到 {len(kl)} 条记录，前 5 条：")
    for item in kl[:5]:
        print(item)

    # 示例：简单测试
    searcher = StockSearcher()

    # 1. 模糊中文
    kw = "宁德"
    result = searcher.search(kw)
    print(f"查询关键字: {kw}")
    print(result)

    # 2. 全名
    kw2 = "宁德时代"
    result2 = searcher.search(kw2)
    print(f"\n查询关键字: {kw2}")
    print(result2)

    # 3. 代码
    kw3 = "300750"
    result3 = searcher.search(kw3)
    print(f"\n查询关键字: {kw3}")
    print(result3)