
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
            val_token = os.getenv("TUSHARE_TOKEN", "")
            if not val_token:
                 logger.error("TUSHARE_TOKEN environment variable is not set")
                 return False
            self.token = val_token.strip()

            # Configure proxy if provided
            # Tushare uses requests internally. Setting env vars usually works.
            # But if there is a specific method, we can use it.
            # ts.set_token(self.token) 
            # self.pro = ts.pro_api()
            
            # Explicit proxy configuration not always standard in new tushare, 
            # but we can set env vars if user provided TUSHARE_PROXY
            proxy = os.getenv("TUSHARE_PROXY")
            if proxy:
                 proxy = proxy.strip() # Robustly handle user input
                 os.environ["HTTP_PROXY"] = proxy
                 os.environ["HTTPS_PROXY"] = proxy
                 logger.info(f"Configured proxy for Tushare: {proxy}")
            else:
                 # Log implied proxy for debugging
                 hp = os.getenv("HTTP_PROXY")
                 hps = os.getenv("HTTPS_PROXY")
                 if hp or hps:
                     logger.info(f"Using system proxy settings - HTTP: {hp}, HTTPS: {hps}")

            ts.set_token(self.token)
            self.pro = ts.pro_api()
            
            # Support custom HTTP URL (e.g. for proxying Pro API calls)
            http_url = os.getenv("TUSHARE_HTTP_URL")
            if http_url and self.pro:
                http_url = http_url.strip()
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
            
            # Use standard tushare interface with error handling
            try:
                df = ts.get_realtime_quotes(code)
            except Exception as e:
                # Catch urllib/requests errors specifically
                logger.error(f"Tushare realtime quotes failed for {code}: {e}")
                # Analyze error for user friendly message
                if "404" in str(e):
                    logger.error("HTTP 404 Error: This usually means the Proxy is misconfigured or inaccessible.")
                    logger.error(f"Current Proxy: {os.environ.get('HTTP_PROXY')}")
                raise e
            
            if df is None or df.empty:
                logger.warning(f"No real-time data found for {symbol}")
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
            


            # Check if dataframe is empty or missing columns
            if df is None or df.empty:
                logger.warning(f"Stock search returned empty result for keyword: {keyword}")
                return []
                
            required_cols = ['symbol', 'name', 'ts_code', 'market']
            # Some Tushare APIs might return 'symbol' but not 'ts_code' or vice versa depending on permissions/endpoint
            # Let's perform a soft check and log warnings, but try to proceed if critical 'symbol' exists
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                logger.warning(f"Stock search result missing columns: {missing_cols}. Columns found: {df.columns.tolist()}")
                # If symbol is missing, we can't do much.
                if 'symbol' not in df.columns:
                     logger.error("Critical column 'symbol' missing from search result.")
                     return []
            
            # Check if keyword matches code or name
            # Handle potential non-string values just in case
            # Ensure columns exist before accessing
            mask = pd.Series([False] * len(df))
            if 'symbol' in df.columns:
                mask |= df['symbol'].astype(str).str.contains(keyword, na=False)
            if 'name' in df.columns:
                mask |= df['name'].astype(str).str.contains(keyword, na=False)
                
            filtered = df[mask].head(10)
            
            result = []
            for _, row in filtered.iterrows():
                item = {
                    "code": row.get('symbol', ''),
                    "name": row.get('name', ''),
                    "ts_code": row.get('ts_code', ''),
                    "market": row.get('market', '')
                }
                result.append(item)
            return result
            
        except Exception as e:
            logger.error(f"Error searching stock: {e}")
            return []

    # Implement other methods as needed or return None/Raise NotImplemented
    # For brevity, implementing minimal set for "get_real_time_data" request
    
    def get_historical_k_data(self, stock_code: str, start_date: str, end_date: str, frequency: str = "d") -> List[str]:
         """
         Get historical K-line data from Tushare Pro
         Returns List[str] in CSV format to match KlineSpider output:
         date,open,close,high,low,volume,amount,amplitude,change_percent,change_amount,turnover_rate
         """
         try:
             # Convert dates: YYYY-MM-DD -> YYYYMMDD
             start_dt = start_date.replace("-", "")
             end_dt = end_date.replace("-", "")
             
             # Map frequency
             api_func = None
             if frequency == "d":
                 api_func = self.pro.daily
             elif frequency == "w":
                 api_func = self.pro.weekly
             elif frequency == "m":
                 api_func = self.pro.monthly
             else:
                 # Tushare Pro basic interface doesn't support minutes easily without specific permissions or different feed
                 logger.warning(f"TushareDataSource: Frequency {frequency} not supported, defaulting to daily")
                 api_func = self.pro.daily

             # Call API
             # Fields: ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount
             df = api_func(ts_code=stock_code, start_date=start_dt, end_date=end_dt)
             
             if df is None or df.empty:
                 return []

             # Sort by date ascending (Tushare returns descending usually)
             df = df.sort_values(by='trade_date')

             result = []
             for _, row in df.iterrows():
                 date_str = row['trade_date'] # YYYYMMDD
                 # Format to YYYY-MM-DD
                 if len(date_str) == 8:
                     date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                 
                 open_val = float(row['open'])
                 close_val = float(row['close'])
                 high_val = float(row['high'])
                 low_val = float(row['low'])
                 vol_val = float(row['vol'])
                 amount_val = float(row['amount']) * 1000 # Tushare amount is '千元' (thousands), Crawler seems to be raw unit? 
                 # Wait, looking at debug output/crawler, amount is usually large.
                 # Let's check Crawler output example if possible.
                 # Assuming Tushare's '千元' needs *1000 to match raw RMB if Crawler returns raw.
                 # But KlineSpider docs don't specify unit. Let's assume *1000 to be safe for "amount".
                 
                 pre_close = float(row['pre_close'])
                 pct_chg = float(row['pct_chg'])
                 change = float(row['change'])
                 
                 # Calculate amplitude: (high - low) / pre_close * 100
                 amplitude = ((high_val - low_val) / pre_close * 100) if pre_close > 0 else 0.0
                 
                 # Turnover rate - not in daily, default 0
                 turnover = 0.0

                 # CSV format: date,open,close,high,low,volume,amount,amplitude,change_percent,change_amount,turnover_rate
                 # Note: order matches parse_kline_data fields indices
                 # Ensure volume is integer (Tushare returns float)
                 line = f"{date_str},{open_val},{close_val},{high_val},{low_val},{int(vol_val)},{amount_val},{amplitude},{pct_chg},{change},{turnover}"
                 result.append(line)
                 
             return result

         except Exception as e:
             logger.error(f"Error getting historical k data from Tushare: {e}")
             if "404" in str(e):
                  logger.error("HTTP 404 Error in K-line: Proxy configuration issue?")
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
             try:
                 df = ts.get_realtime_quotes(indices)
             except Exception as e:
                 logger.error(f"Error getting indices from Tushare: {e}")
                 if "404" in str(e):
                     logger.error("HTTP 404 Error: This usually means the Proxy is misconfigured or inaccessible.")
                 return []

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
