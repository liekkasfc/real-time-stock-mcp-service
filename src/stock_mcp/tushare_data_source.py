
import logging
import os
import tushare as ts
import pandas as pd
from typing import List, Optional, Dict, Any
from stock_mcp.data_source_interface import FinancialDataInterface, DataSourceError, NoDataFoundError

logger = logging.getLogger(__name__)

class TushareDataSource(FinancialDataInterface):
    def __init__(self):
        self.pro = None
        self.token = None

    def initialize(self) -> bool:
        """
        Initialize Tushare Pro API
        """
        try:
            self.token = os.getenv("TUSHARE_TOKEN")
            if not self.token:
                logger.error("TUSHARE_TOKEN environment variable is not set")
                return False

            # Configure proxy if provided
            # Tushare uses requests internally. Setting env vars usually works.
            # But if there is a specific method, we can use it.
            # ts.set_token(self.token) 
            # self.pro = ts.pro_api()
            
            # Explicit proxy configuration not always standard in new tushare, 
            # but we can set env vars if user provided TUSHARE_PROXY
            proxy = os.getenv("TUSHARE_PROXY")
            if proxy:
                 os.environ["HTTP_PROXY"] = proxy
                 os.environ["HTTPS_PROXY"] = proxy
                 logger.info(f"Configured proxy for Tushare: {proxy}")

            ts.set_token(self.token)
            self.pro = ts.pro_api()
            
            # Support custom HTTP URL (e.g. for proxying Pro API calls)
            http_url = os.getenv("TUSHARE_HTTP_URL")
            if http_url and self.pro:
                logger.info(f"Configuring custom Tushare HTTP URL: {http_url}")
                # Monkeypatch the private variable in DataApi instance
                # Name mangling: _DataApi__http_url
                try:
                    self.pro._DataApi__http_url = http_url
                except AttributeError:
                    logger.warning("Could not set custom HTTP URL: _DataApi__http_url not found")
            
            logger.info("Tushare Pro API initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Tushare API: {e}")
            return False

    def cleanup(self):
        pass

    def get_real_time_data(self, symbol: str) -> Dict:
        """
        Get real-time data using Tushare legacy API (get_realtime_quotes)
        Symbol format: "600519.SH" -> "600519" (Tushare legacy usually takes code only for A-share, 
        or need to check documentation. get_realtime_quotes takes code list).
        """
        try:
            # Tushare legacy get_realtime_quotes usually takes a list of codes.
            # It expects codes like '600519', 'sh600519'?
            # Let's try to parse the symbol.
            # Input symbol e.g. "600519.SH"
            code = symbol.split(".")[0]
            
            # Use standard tushare interface
            df = ts.get_realtime_quotes(code)
            
            if df is None or df.empty:
                raise NoDataFoundError(f"No real-time data found for {symbol}")
                
            row = df.iloc[0]
            
            # Map Tushare fields to our format
            # name, open, pre_close, price, high, low, bid, ask, volume, amount, date, time
            
            data = {
                "name": row['name'],
                "code": row['code'],
                "open": float(row['open']),
                "pre_close": float(row['pre_close']),
                "price": float(row['price']),
                "high": float(row['high']),
                "low": float(row['low']),
                "volume": float(row['volume']),
                "amount": float(row['amount']),
                "date": row['date'],
                "time": row['time']
            }
            
            # Calculate change
            change_amount = data['price'] - data['pre_close']
            change_percent = (change_amount / data['pre_close']) * 100 if data['pre_close'] != 0 else 0
             
            # Construct dictionary similar to WebCrawlerDataSource format for compatibility
            result = {
                "name": data['name'],
                "code": symbol, # Keep original symbol with .SH/.SZ
                "klines": [
                    f"{data['date']} {data['time']},{data['open']},{data['price']},{data['high']},{data['low']},{int(data['volume'])},{data['amount']},{0},{change_percent},{change_amount},{0}"
                ],
                "preKPrice": data['pre_close']
            }
            
            return result

        except Exception as e:
            logger.error(f"Error getting real-time data from Tushare: {e}")
            raise DataSourceError(str(e))

    def get_stock_search(self, keyword: str) -> Optional[List[Dict]]:
        """
        Search stock using Pro API
        """
        try:
            # stock_basic
            # fields: ts_code, symbol, name, area, industry, market, list_date
            df = self.pro.stock_basic(fields='ts_code,symbol,name,market')
            
            # Filter in memory (not efficient for large query but ok for search)
            # Or use Tushare params if possible. ts_code only supports specific code.
            # We filter dataframe.
            
            # Check if keyword matches code or name
            mask = df['symbol'].str.contains(keyword) | df['name'].str.contains(keyword)
            filtered = df[mask].head(10)
            
            result = []
            for _, row in filtered.iterrows():
                result.append({
                    "code": row['symbol'],
                    "name": row['name'],
                    "ts_code": row['ts_code'],
                    "market": row['market']
                })
            return result
            
        except Exception as e:
            logger.error(f"Error searching stock: {e}")
            return []

    # Implement other methods as needed or return None/Raise NotImplemented
    # For brevity, implementing minimal set for "get_real_time_data" request
    
    def get_historical_k_data(self, stock_code: str, start_date: str, end_date: str, frequency: str = "d") -> List[Dict]:
         # ... implementation ...
         return []

    def get_technical_indicators(self, stock_code: str, page_size: int = 30) -> List[Dict]:
        return []

    def get_last_trading_day(self) -> Optional[Dict]:
        return None

    def get_main_business(self, stock_code: str, report_date: Optional[str] = None) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_report_dates(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_business_scope(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        return None

    def get_business_review(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        return None

    def get_valuation_analysis(self, stock_code: str, date_type: int = 3) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_institutional_rating(self, stock_code: str, begin_time: str, end_time: str) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_main_financial_data(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        return None

    def get_financial_summary(self, stock_code: str, date_type_code: str = "004") -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_holder_number(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return None
        
    def get_industry_profit_comparison(self, stock_code: str, report_date: str = None) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_financial_ratios(self, stock_code: str, report_dates: List[str] = None) -> Optional[List[Dict[Any, Any]]]:
        return None
        
    def get_plate_quotation(self, plate_type: int = 2, page_size: int = 10) -> List[Dict]:
        return []
        
    def get_plate_fund_flow(self, plate_type: int = 2, page_size: int = 10) -> List[Dict]:
        return []
        
    def get_historical_fund_flow(self, stock_code: str, limit: int = 10) -> Optional[Dict]:
        return None
        
    def get_billboard_data(self, trade_date: str, page_size: int = 10) -> List[Dict]:
         return []

    def get_stock_billboard_data(self, stock_code: str, page_size: int = 10) -> List[Dict]:
        return []
        
    def get_growth_comparison(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_dupont_analysis_comparison(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
         return None

    def get_valuation_comparison(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return None
        
    def get_market_performance(self, secucode: str) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_current_plate_changes(self, page_size: int = 10) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_current_count_changes(self) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_macroeconomic_research(self, begin_time: str, end_time: str) -> Optional[List[Dict[Any, Any]]]:
        return None
        
    def get_real_time_market_indices(self) -> List[Dict]:
        """
        Get real-time market indices
        """
        try:
             # Typical indices
             indices = ['sh', 'sz', 'hs300', 'sz50', 'zxb', 'cyb']
             df = ts.get_realtime_quotes(indices)
             
             result = []
             if df is not None and not df.empty:
                 for _, row in df.iterrows():
                     # Format similar to WebCrawlerDataSource
                     # WebCrawlerDataSource: f12 code, f14 name, f2 point/100, f3 %, f4 change
                     # Tushare: name, price, pre_close
                     
                     price = float(row['price'])
                     pre_close = float(row['pre_close'])
                     change = price - pre_close
                     change_pct = (change / pre_close) * 100 if pre_close != 0 else 0
                     
                     result.append({
                         "f12": row['code'],
                         "f14": row['name'],
                         "f2": int(price * 100),
                         "f3": int(change_pct * 100),
                         "f4": int(change * 100)
                     })
             return result
        except Exception as e:
            logger.error(f"Error getting indices: {e}")
            return []

    def get_smart_score(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        return None

    def get_smart_score_rank(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        return None

    def get_top_rated_stocks(self, page_size: int = 10) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_main_force_control(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_participation_wish(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return None

    def get_intraday_changes(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return None
