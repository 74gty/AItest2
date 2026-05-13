from datetime import date

from findata_service.cache import MemoryCache
from findata_service.errors import FindataError
from findata_service.validators import validate_date_range


class MockDataSource:
    name = "mock"

    def __init__(self):
        self.stock_prices = {
            "600519": {"name": "贵州茅台", "price": 1688.88, "change_pct": -2.6},
            "000001": {"name": "平安银行", "price": 10.25, "change_pct": 1.2},
        }
        self.fund_navs = {
            "000001": {"name": "华夏成长混合", "nav": 1.2345, "fund_type": "混合型", "nav_date": "20240510"},
            "110022": {"name": "易方达消费行业股票", "nav": 3.4567, "fund_type": "股票型", "nav_date": "20240510"},
        }

    def stock_realtime(self, symbol):
        if symbol not in self.stock_prices:
            raise FindataError("DATA_NOT_FOUND", "未找到股票行情", status_code=404, details={"symbol": symbol})
        item = self.stock_prices[symbol]
        return {
            "symbol": symbol,
            "name": item["name"],
            "price": item["price"],
            "change_pct": item["change_pct"],
            "source": self.name,
        }

    def stock_history(self, symbol, start_date, end_date):
        validate_date_range(start_date, end_date)
        if symbol not in self.stock_prices:
            raise FindataError("DATA_NOT_FOUND", "未找到股票历史行情", status_code=404, details={"symbol": symbol})
        return {
            "symbol": symbol,
            "items": [
                {"date": start_date, "open": 1650.0, "close": 1668.0, "high": 1680.0, "low": 1640.0, "volume": 120000},
                {"date": end_date, "open": 1668.0, "close": 1688.88, "high": 1700.0, "low": 1660.0, "volume": 118000},
            ],
            "source": self.name,
        }

    def index_history(self, symbol, start_date, end_date):
        validate_date_range(start_date, end_date)
        if not symbol.startswith(("sh", "sz")):
            raise FindataError("INVALID_SYMBOL", "指数代码必须以 sh 或 sz 开头")
        return {
            "symbol": symbol,
            "items": [
                {"date": start_date, "close": 3500.12, "change_pct": 0.3},
                {"date": end_date, "close": 3560.55, "change_pct": -0.4},
            ],
            "source": self.name,
        }

    def trade_calendar(self, start_date, end_date):
        start, end = validate_date_range(start_date, end_date)
        days = []
        current = start
        while current <= end:
            days.append({"date": current.strftime("%Y%m%d"), "is_trading_day": current.weekday() < 5})
            current = date.fromordinal(current.toordinal() + 1)
        return {"items": days, "source": self.name}

    def fund_basic(self, fund_code):
        if fund_code not in self.fund_navs:
            raise FindataError("DATA_NOT_FOUND", "未找到基金信息", status_code=404, details={"fund_code": fund_code})
        fund = self.fund_navs[fund_code]
        return {"fund_code": fund_code, "name": fund["name"], "fund_type": fund["fund_type"], "source": self.name}

    def fund_nav(self, fund_code):
        if fund_code not in self.fund_navs:
            raise FindataError("DATA_NOT_FOUND", "未找到基金净值", status_code=404, details={"fund_code": fund_code})
        fund = self.fund_navs[fund_code]
        return {
            "fund_code": fund_code,
            "name": fund["name"],
            "nav": fund["nav"],
            "nav_date": fund["nav_date"],
            "source": self.name,
        }

    def fund_history(self, fund_code, start_date, end_date):
        validate_date_range(start_date, end_date)
        self.fund_nav(fund_code)
        return {
            "fund_code": fund_code,
            "items": [
                {"date": start_date, "nav": 1.2, "accumulated_nav": 1.9},
                {"date": end_date, "nav": self.fund_navs[fund_code]["nav"], "accumulated_nav": 1.95},
            ],
            "source": self.name,
        }


class AkShareDataSource:
    name = "akshare"

    def __init__(self):
        try:
            import akshare as ak
        except ImportError as error:
            raise FindataError("DATASOURCE_UNAVAILABLE", "AKShare 未安装或不可用") from error
        self.ak = ak

    def stock_realtime(self, symbol):
        frame = self.ak.stock_zh_a_spot_em()
        row = frame[frame["代码"].astype(str) == symbol]
        if row.empty:
            raise FindataError("DATA_NOT_FOUND", "AKShare 未找到股票行情", status_code=404, details={"symbol": symbol})
        item = row.iloc[0].to_dict()
        return {
            "symbol": symbol,
            "name": str(item.get("名称", "")),
            "price": float(item.get("最新价", 0) or 0),
            "change_pct": float(item.get("涨跌幅", 0) or 0),
            "source": self.name,
        }

    def stock_history(self, symbol, start_date, end_date):
        frame = self.ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date)
        return {"symbol": symbol, "items": self._records(frame), "source": self.name}

    def index_history(self, symbol, start_date, end_date):
        market = "sh" if symbol.startswith("sh") else "sz"
        code = symbol[2:] if symbol.startswith(("sh", "sz")) else symbol
        frame = self.ak.stock_zh_index_daily(symbol=f"{market}{code}")
        if "date" in frame.columns:
            frame = frame[(frame["date"] >= start_date) & (frame["date"] <= end_date)]
        return {"symbol": symbol, "items": self._records(frame), "source": self.name}

    def trade_calendar(self, start_date, end_date):
        start, end = validate_date_range(start_date, end_date)
        frame = self.ak.tool_trade_date_hist_sina()
        records = []
        for item in self._records(frame):
            raw_date = str(item.get("trade_date", item.get("date", ""))).replace("-", "")
            if start_date <= raw_date <= end_date:
                records.append({"date": raw_date, "is_trading_day": True})
        if not records:
            current = start
            while current <= end:
                records.append({"date": current.strftime("%Y%m%d"), "is_trading_day": current.weekday() < 5})
                current = date.fromordinal(current.toordinal() + 1)
        return {"items": records, "source": self.name}

    def fund_basic(self, fund_code):
        frame = self.ak.fund_name_em()
        row = frame[frame["基金代码"].astype(str) == fund_code]
        if row.empty:
            raise FindataError("DATA_NOT_FOUND", "AKShare 未找到基金信息", status_code=404, details={"fund_code": fund_code})
        item = row.iloc[0].to_dict()
        return {
            "fund_code": fund_code,
            "name": str(item.get("基金简称", "")),
            "fund_type": str(item.get("基金类型", "")),
            "source": self.name,
        }

    def fund_nav(self, fund_code):
        frame = self.ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        if frame.empty:
            raise FindataError("DATA_NOT_FOUND", "AKShare 未找到基金净值", status_code=404, details={"fund_code": fund_code})
        item = frame.iloc[-1].to_dict()
        return {
            "fund_code": fund_code,
            "name": self.fund_basic(fund_code).get("name", fund_code),
            "nav": float(item.get("单位净值", item.get("净值", 0)) or 0),
            "nav_date": str(item.get("净值日期", item.get("日期", ""))).replace("-", ""),
            "source": self.name,
        }

    def fund_history(self, fund_code, start_date, end_date):
        validate_date_range(start_date, end_date)
        frame = self.ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        records = []
        for item in self._records(frame):
            raw_date = str(item.get("净值日期", item.get("日期", ""))).replace("-", "")
            if start_date <= raw_date <= end_date:
                records.append({
                    "date": raw_date,
                    "nav": float(item.get("单位净值", item.get("净值", 0)) or 0),
                    "accumulated_nav": float(item.get("累计净值", item.get("累计净值走势", 0)) or 0),
                })
        return {"fund_code": fund_code, "items": records, "source": self.name}

    def _records(self, frame):
        return frame.fillna("").to_dict("records")


class BaoStockDataSource:
    name = "baostock"

    def __init__(self):
        try:
            import baostock as bs
        except ImportError as error:
            raise FindataError("DATASOURCE_UNAVAILABLE", "BaoStock 未安装或不可用") from error
        self.bs = bs

    def stock_history(self, symbol, start_date, end_date):
        code = self._to_baostock_code(symbol)
        return self._query_history(code, symbol, start_date, end_date)

    def index_history(self, symbol, start_date, end_date):
        code = symbol if "." in symbol else f"{symbol[:2]}.{symbol[2:]}"
        return self._query_history(code, symbol, start_date, end_date)

    def _query_history(self, code, symbol, start_date, end_date):
        login_result = self.bs.login()
        if getattr(login_result, "error_code", "0") != "0":
            raise FindataError("DATASOURCE_UNAVAILABLE", "BaoStock 登录失败")
        try:
            result = self.bs.query_history_k_data_plus(
                code,
                "date,open,high,low,close,volume",
                start_date=f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}",
                end_date=f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}",
                frequency="d",
                adjustflag="3",
            )
            rows = []
            while result.next():
                item = dict(zip(result.fields, result.get_row_data()))
                rows.append({
                    "date": item["date"].replace("-", ""),
                    "open": float(item["open"] or 0),
                    "high": float(item["high"] or 0),
                    "low": float(item["low"] or 0),
                    "close": float(item["close"] or 0),
                    "volume": float(item["volume"] or 0),
                })
            if not rows:
                raise FindataError("DATA_NOT_FOUND", "BaoStock 未找到历史行情", status_code=404)
            return {"symbol": symbol, "items": rows, "source": self.name}
        finally:
            self.bs.logout()

    def _to_baostock_code(self, symbol):
        prefix = "sh" if symbol.startswith("6") else "sz"
        return f"{prefix}.{symbol}"


class ResilientDataSource:
    def __init__(self, primary, fallback=None, cache=None):
        self.primary = primary
        self.fallback = fallback
        self.cache = cache or MemoryCache()

    def call(self, operation, *args):
        key = (operation, args)
        cached = self.cache.get(key)
        try:
            value = getattr(self.primary, operation)(*args)
            self.cache.set(key, value)
            return value
        except (AttributeError, FindataError) as primary_error:
            if cached:
                cached["source"] = "cache"
                return cached
            if self.fallback and hasattr(self.fallback, operation):
                try:
                    value = getattr(self.fallback, operation)(*args)
                    self.cache.set(key, value)
                    return value
                except FindataError:
                    pass
            raise primary_error
