
import logging
from typing import List, Optional, Dict, Any
from stock_mcp.data_source_interface import FinancialDataInterface, DataSourceError

logger = logging.getLogger(__name__)

class HybridDataSource(FinancialDataInterface):
    """
    A hybrid data source that uses a primary source (Crawler) by default,
    but falls back to a secondary source (Tushare) for specific methods
    if the primary fails.
    """

    def __init__(self, primary: FinancialDataInterface, secondary: Optional[FinancialDataInterface] = None):
        self.primary = primary
        self.secondary = secondary

    def initialize(self) -> bool:
        """Initialize both data sources."""
        p_success = self.primary.initialize()
        s_success = True
        if self.secondary:
            s_success = self.secondary.initialize()
        
        if not p_success and not s_success:
            logger.error("Both primary and secondary data sources failed to initialize.")
            return False
        
        if not p_success:
            logger.warning("Primary data source failed to initialize. Functionality may be limited.")
        
        return True

    def cleanup(self):
        """Cleanup both data sources."""
        if self.primary:
            self.primary.cleanup()
        if self.secondary:
            self.secondary.cleanup()

    def get_real_time_data(self, symbol: str) -> Dict:
        """
        Get real-time data with fallback mechanism.
        """
        try:
            return self.primary.get_real_time_data(symbol)
        except Exception as e:
            logger.warning(f"Primary source (Crawler) failed for realtime data: {e}")
            
            if self.secondary:
                logger.info("Attempting to switch to secondary source (Tushare)...")
                try:
                    return self.secondary.get_real_time_data(symbol)
                except Exception as e2:
                    logger.error(f"Secondary source (Tushare) also failed: {e2}")
                    raise e2 # Raise the last error if both fail
            else:
                logger.warning("No secondary source configured to fall back to.")
                raise e

    # Delegate all other methods to primary source by default
    # If primary fails for these, we currently DON'T fall back unless explicitly implemented
    
    def get_stock_search(self, keyword: str) -> Optional[List[Dict]]:
        # Tushare search is also good, but for now duplicate logic only where necessary
        return self.primary.get_stock_search(keyword)

    def get_historical_k_data(self, stock_code: str, start_date: str, end_date: str, frequency: str = "d") -> List[Dict]:
        return self.primary.get_historical_k_data(stock_code, start_date, end_date, frequency)

    def get_technical_indicators(self, stock_code: str, page_size: int = 30) -> List[Dict]:
        return self.primary.get_technical_indicators(stock_code, page_size)

    def get_last_trading_day(self) -> Optional[Dict]:
        return self.primary.get_last_trading_day()

    def get_main_business(self, stock_code: str, report_date: Optional[str] = None) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_main_business(stock_code, report_date)

    def get_report_dates(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_report_dates(stock_code)

    def get_business_scope(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        return self.primary.get_business_scope(stock_code)

    def get_business_review(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        return self.primary.get_business_review(stock_code)

    def get_valuation_analysis(self, stock_code: str, date_type: int = 3) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_valuation_analysis(stock_code, date_type)

    def get_institutional_rating(self, stock_code: str, begin_time: str, end_time: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_institutional_rating(stock_code, begin_time, end_time)

    def get_main_financial_data(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        return self.primary.get_main_financial_data(stock_code)

    def get_financial_summary(self, stock_code: str, date_type_code: str = "004") -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_financial_summary(stock_code, date_type_code)

    def get_holder_number(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_holder_number(stock_code)

    def get_industry_profit_comparison(self, stock_code: str, report_date: str = None) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_industry_profit_comparison(stock_code, report_date)

    def get_financial_ratios(self, stock_code: str, report_dates: List[str] = None) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_financial_ratios(stock_code, report_dates)

    def get_plate_quotation(self, plate_type: int = 2, page_size: int = 10) -> List[Dict]:
        return self.primary.get_plate_quotation(plate_type, page_size)

    def get_plate_fund_flow(self, plate_type: int = 2, page_size: int = 10) -> List[Dict]:
        return self.primary.get_plate_fund_flow(plate_type, page_size)

    def get_historical_fund_flow(self, stock_code: str, limit: int = 10) -> Optional[Dict]:
        return self.primary.get_historical_fund_flow(stock_code, limit)

    def get_billboard_data(self, trade_date: str, page_size: int = 10) -> List[Dict]:
        return self.primary.get_billboard_data(trade_date, page_size)

    def get_stock_billboard_data(self, stock_code: str, limit: int = 10) -> List[Dict]:
        return self.primary.get_stock_billboard_data(stock_code, limit)

    def get_growth_comparison(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_growth_comparison(stock_code)

    def get_dupont_analysis_comparison(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_dupont_analysis_comparison(stock_code)

    def get_valuation_comparison(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_valuation_comparison(stock_code)

    def get_market_performance(self, secucode: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_market_performance(secucode)

    def get_current_plate_changes(self, page_size: int = 10) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_current_plate_changes(page_size)

    def get_current_count_changes(self) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_current_count_changes()

    def get_macroeconomic_research(self, begin_time: str, end_time: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_macroeconomic_research(begin_time, end_time)

    def get_real_time_market_indices(self) -> List[Dict]:
        try:
            return self.primary.get_real_time_market_indices()
        except Exception as e:
            logger.warning(f"Primary source failed for market indices: {e}")
            if self.secondary:
                 # Note: TushareDataSource's get_real_time_market_indices implementation
                 # might need to match the return format exactly.
                 # Assuming TushareDataSource implements this correctly as per interface.
                 return self.secondary.get_real_time_market_indices()
            raise e

    def get_smart_score(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        return self.primary.get_smart_score(stock_code)

    def get_smart_score_rank(self, stock_code: str) -> Optional[Dict[Any, Any]]:
        return self.primary.get_smart_score_rank(stock_code)

    def get_top_rated_stocks(self, page_size: int = 10) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_top_rated_stocks(page_size)

    def get_main_force_control(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_main_force_control(stock_code)

    def get_participation_wish(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_participation_wish(stock_code)

    def get_intraday_changes(self, stock_code: str) -> Optional[List[Dict[Any, Any]]]:
        return self.primary.get_intraday_changes(stock_code)
