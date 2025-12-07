from src.crawler.valuation_data import ValuationDataCrawler
import datetime

# 测试估值分析数据
valuation_crawler = ValuationDataCrawler()

# 测试默认参数（市盈率TTM，5年周期）
# print("测试默认参数（市盈率TTM，5年周期）:")
# valuation_data = valuation_crawler.get_valuation_analysis("688041.SH")
# print(valuation_data)
#
# # 测试市净率MRQ，3年周期
# print("\n测试市净率MRQ，3年周期:")
# pb_data = valuation_crawler.get_valuation_analysis(
#     "688041.SH",
#     ValuationDataCrawler.INDICATOR_TYPE_PB_MRQ,
#     ValuationDataCrawler.DATE_TYPE_3YEAR
# )
# print(pb_data)
#
# # 测试市销率TTM，10年周期
# print("\n测试市销率TTM，10年周期:")
# ps_data = valuation_crawler.get_valuation_analysis(
#     "688041.SH",
#     ValuationDataCrawler.INDICATOR_TYPE_PS_TTM,
#     ValuationDataCrawler.DATE_TYPE_10YEAR
# )
# print(ps_data)

# 测试机构评级功能
print("\n测试机构评级功能:")
# 设置正确的日期范围（开始日期应该早于结束日期）
start_date = "2025-10-23"
end_date = "2025-12-07"
institutional_rating_data = valuation_crawler.get_institutional_rating("688041", start_date, end_date)
print(institutional_rating_data)