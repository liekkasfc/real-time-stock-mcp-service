from src.crawler.fundamental_data import FundamentalDataCrawler

crawler = FundamentalDataCrawler()
r = crawler.get_main_business("000021.SZ", "2025-06-30")
print(r)