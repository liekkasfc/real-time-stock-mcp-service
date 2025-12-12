import json
import re

from src.crawler.base_crawler import EastMoneyBaseSpider

import requests
from typing import Optional, Dict, Any, List


class SmartReviewCrawler(EastMoneyBaseSpider):
    """
    智能点评数据爬虫类

    用于获取股票的智能分析点评信息
    """
    
    SMART_REVIEW_URL = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
    EXPERT_REVIEW_URL = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
    SMART_SCORE_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

    def __init__(
            self,
            session: Optional[requests.Session] = None,
            timeout: int = 10,
    ):
        """
        初始化智能点评数据爬虫
        
        :param session: requests.Session 实例
        :param timeout: 请求超时时间
        """
        super().__init__(session, timeout)

    def get_smart_score(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        """
        获取股票智能评分数据
        
        :param stock_code: 股票代码
        :return: 智能评分数据字典
        """
        # 生成 callback 参数
        callback = self._generate_callback()
        
        params = {
            "callback": callback,
            "filter": f"(SECURITY_CODE=\"{stock_code}\")",
            "columns": "ALL",
            "source": "WEB",
            "client": "WEB",
            "reportName": "RPT_CUSTOM_STOCK_PK"
        }
        
        try:
            response = self._get_jsonp(self.SMART_SCORE_URL, params)
            # 检查响应是否成功
            if response and response.get("code") == 0 and response.get("success") is True:
                data = response.get("result", {}).get("data", [])
                return data[0] if data else None
            else:
                # 如果不成功，返回错误信息
                message = response.get("message", "未知错误") if response else "未知错误"
                return {"error": message}
        except Exception as e:
            return {"error": str(e)}