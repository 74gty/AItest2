from datetime import date
from uuid import uuid4

from findata_service.data_sources import MockDataSource, ResilientDataSource
from findata_service.errors import FindataError
from findata_service.validators import validate_fund_code, validate_symbol


class FindataService:
    def __init__(self, data_source=None):
        self.data_source = data_source or ResilientDataSource(MockDataSource())
        self.watchlist = {}
        self.holdings = {}

    def stock_realtime(self, symbol):
        symbol = validate_symbol(symbol)
        return self.data_source.call("stock_realtime", symbol)

    def stock_history(self, symbol, start_date, end_date):
        symbol = validate_symbol(symbol)
        return self.data_source.call("stock_history", symbol, start_date, end_date)

    def index_history(self, symbol, start_date, end_date):
        symbol = validate_symbol(symbol)
        return self.data_source.call("index_history", symbol, start_date, end_date)

    def trade_calendar(self, start_date, end_date):
        return self.data_source.call("trade_calendar", start_date, end_date)

    def fund_basic(self, fund_code):
        fund_code = validate_fund_code(fund_code)
        return self.data_source.call("fund_basic", fund_code)

    def fund_nav(self, fund_code):
        fund_code = validate_fund_code(fund_code)
        item = self.data_source.call("fund_nav", fund_code)
        if item["nav_date"] > date.today().strftime("%Y%m%d"):
            raise FindataError("INVALID_NAV_DATE", "基金净值日期不能晚于当前日期")
        return item

    def fund_history(self, fund_code, start_date, end_date):
        fund_code = validate_fund_code(fund_code)
        return self.data_source.call("fund_history", fund_code, start_date, end_date)

    def add_watchlist(self, item_type, symbol, name=None):
        symbol = validate_symbol(symbol)
        key = (item_type, symbol)
        if key in [(item["item_type"], item["symbol"]) for item in self.watchlist.values()]:
            raise FindataError("DUPLICATE_WATCHLIST_ITEM", "自选关注已存在", status_code=409)
        if item_type == "fund":
            self.fund_basic(symbol)
        elif item_type == "stock":
            self.stock_realtime(symbol)
        item_id = uuid4().hex
        item = {"item_id": item_id, "item_type": item_type, "symbol": symbol, "name": name or symbol}
        self.watchlist[item_id] = item
        return item

    def delete_watchlist(self, item_id):
        if item_id not in self.watchlist:
            raise FindataError("WATCHLIST_ITEM_NOT_FOUND", "自选关注不存在", status_code=404)
        return self.watchlist.pop(item_id)

    def list_watchlist(self):
        return list(self.watchlist.values())

    def add_holding(self, item_type, symbol, quantity, cost_price, name=None):
        symbol = validate_symbol(symbol)
        item_id = uuid4().hex
        holding = {
            "holding_id": item_id,
            "item_type": item_type,
            "symbol": symbol,
            "quantity": quantity,
            "cost_price": cost_price,
            "name": name or symbol,
        }
        self.holdings[item_id] = holding
        return holding

    def portfolio_summary(self):
        rows = []
        total_market_value = 0
        for holding in self.holdings.values():
            current_price = self._current_price(holding)
            cost_value = holding["quantity"] * holding["cost_price"]
            market_value = holding["quantity"] * current_price
            total_market_value += market_value
            rows.append({**holding, "current_price": current_price, "cost_value": cost_value, "market_value": market_value})

        for row in rows:
            row["profit"] = round(row["market_value"] - row["cost_value"], 4)
            row["profit_rate"] = round(row["profit"] / row["cost_value"], 6)
            row["asset_weight"] = round(row["market_value"] / total_market_value, 6) if total_market_value else 0

        return {"total_market_value": round(total_market_value, 4), "holdings": rows}

    def risk_alerts(self):
        alerts = []
        for holding in self.holdings.values():
            if holding["item_type"] == "stock":
                realtime = self.stock_realtime(holding["symbol"])
                if realtime["change_pct"] <= -2:
                    alerts.append({
                        "symbol": holding["symbol"],
                        "risk_type": "PRICE_DROP",
                        "level": "MEDIUM",
                        "message": "股票跌幅超过阈值",
                    })
            if holding["item_type"] == "fund":
                nav = self.fund_nav(holding["symbol"])
                if nav["nav_date"] < date.today().strftime("%Y%m%d"):
                    alerts.append({
                        "symbol": holding["symbol"],
                        "risk_type": "NAV_STALE",
                        "level": "LOW",
                        "message": "基金净值不是当日更新",
                    })
        return alerts

    def health(self):
        return {"status": "ok", "mode": "mock", "data_source": "mock"}

    def _current_price(self, holding):
        if holding["item_type"] == "fund":
            return self.fund_nav(holding["symbol"])["nav"]
        return self.stock_realtime(holding["symbol"])["price"]
