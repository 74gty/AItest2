import pytest

from findata_service.cache import MemoryCache
from findata_service.data_sources import ResilientDataSource
from findata_service.errors import FindataError
from findata_service.service import FindataService


pytestmark = pytest.mark.findata


@pytest.fixture
def service():
    return FindataService()


def test_stock_realtime_query(service):
    data = service.stock_realtime("600519")

    assert data["symbol"] == "600519"
    assert isinstance(data["price"], float)
    assert data["source"] == "mock"


def test_stock_history_rejects_invalid_date_range(service):
    with pytest.raises(FindataError) as error:
        service.stock_history("600519", "20241231", "20240101")

    assert error.value.code == "INVALID_DATE_RANGE"


def test_trade_calendar_marks_weekend(service):
    data = service.trade_calendar("20240510", "20240512")

    days = {item["date"]: item["is_trading_day"] for item in data["items"]}
    assert days["20240510"] is True
    assert days["20240511"] is False
    assert days["20240512"] is False


def test_fund_nav_date_is_not_future(service):
    data = service.fund_nav("000001")

    assert data["fund_code"] == "000001"
    assert data["nav_date"] <= "20260513"


def test_watchlist_add_duplicate_and_delete(service):
    item = service.add_watchlist("stock", "600519", "贵州茅台")

    with pytest.raises(FindataError) as error:
        service.add_watchlist("stock", "600519", "贵州茅台")
    assert error.value.code == "DUPLICATE_WATCHLIST_ITEM"

    deleted = service.delete_watchlist(item["item_id"])
    assert deleted["symbol"] == "600519"
    assert service.list_watchlist() == []


def test_watchlist_rejects_illegal_code(service):
    with pytest.raises(FindataError) as error:
        service.add_watchlist("stock", "999999")

    assert error.value.code == "DATA_NOT_FOUND"


def test_portfolio_summary_calculates_profit_and_weight(service):
    service.add_holding("stock", "600519", quantity=2, cost_price=1600)
    service.add_holding("fund", "000001", quantity=1000, cost_price=1.2)

    summary = service.portfolio_summary()

    assert summary["total_market_value"] > 0
    assert len(summary["holdings"]) == 2
    assert sum(item["asset_weight"] for item in summary["holdings"]) == pytest.approx(1, rel=0.00001)


def test_risk_alerts_include_price_drop_and_stale_nav(service):
    service.add_holding("stock", "600519", quantity=1, cost_price=1600)
    service.add_holding("fund", "000001", quantity=1000, cost_price=1.2)

    alerts = service.risk_alerts()
    risk_types = {item["risk_type"] for item in alerts}

    assert "PRICE_DROP" in risk_types
    assert "NAV_STALE" in risk_types


def test_unified_error_shape():
    error = FindataError("INVALID_SYMBOL", "股票代码不能为空", details={"symbol": ""})

    assert error.code == "INVALID_SYMBOL"
    assert error.details == {"symbol": ""}


class FailingSource:
    def __init__(self):
        self.name = "failing"
        self.calls = 0

    def stock_realtime(self, symbol):
        self.calls += 1
        if self.calls == 1:
            return {"symbol": symbol, "name": "缓存样本", "price": 1.0, "change_pct": 0.0, "source": self.name}
        raise FindataError("DATASOURCE_UNAVAILABLE", "数据源失败")


class FallbackSource:
    def stock_realtime(self, symbol):
        return {"symbol": symbol, "name": "降级样本", "price": 2.0, "change_pct": 0.0, "source": "fallback"}


def test_cache_degrades_when_primary_fails():
    source = FailingSource()
    data_source = ResilientDataSource(source, cache=MemoryCache())

    first = data_source.call("stock_realtime", "600519")
    second = data_source.call("stock_realtime", "600519")

    assert first["source"] == "failing"
    assert second["source"] == "cache"


def test_fallback_degrades_when_cache_missing():
    data_source = ResilientDataSource(FailingSource(), fallback=FallbackSource(), cache=MemoryCache())
    data_source.primary.calls = 1

    data = data_source.call("stock_realtime", "600519")

    assert data["source"] == "fallback"
