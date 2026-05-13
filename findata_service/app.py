from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from findata_service.errors import FindataError, error_response
from findata_service.factory import create_findata_source
from findata_service.models import HoldingRequest, WatchlistRequest
from findata_service.service import FindataService


app = FastAPI(title="EUTL 金融行情数据聚合与风险监控测试平台")
service = FindataService(data_source=create_findata_source())
INDEX_TEMPLATE = Path(__file__).resolve().parent / "templates" / "index.html"


def query_service(mode: str = "mock"):
    # mode 只影响本次查询，避免网页体验真实数据时破坏 CI 默认 Mock 稳定性
    if mode == "live":
        return FindataService(data_source=create_findata_source("live"))
    return service


@app.exception_handler(FindataError)
def handle_findata_error(request: Request, error: FindataError):
    return JSONResponse(status_code=error.status_code, content=error_response(error))


@app.get("/")
def root():
    # 浏览器打开根路径时给出服务入口，避免体验时看到 404
    return HTMLResponse(INDEX_TEMPLATE.read_text(encoding="utf-8"))


@app.get("/api/health")
def health():
    return {"success": True, "data": service.health()}


@app.get("/api/stock/realtime")
def stock_realtime(symbol: str = "", mode: str = "mock"):
    return {"success": True, "data": query_service(mode).stock_realtime(symbol)}


@app.get("/api/stock/history")
def stock_history(symbol: str = "", start_date: str = "", end_date: str = "", mode: str = "mock"):
    return {"success": True, "data": query_service(mode).stock_history(symbol, start_date, end_date)}


@app.get("/api/index/history")
def index_history(symbol: str = "", start_date: str = "", end_date: str = "", mode: str = "mock"):
    return {"success": True, "data": query_service(mode).index_history(symbol, start_date, end_date)}


@app.get("/api/trade/calendar")
def trade_calendar(start_date: str = "", end_date: str = "", mode: str = "mock"):
    return {"success": True, "data": query_service(mode).trade_calendar(start_date, end_date)}


@app.get("/api/fund/basic")
def fund_basic(fund_code: str = "", mode: str = "mock"):
    return {"success": True, "data": query_service(mode).fund_basic(fund_code)}


@app.get("/api/fund/nav")
def fund_nav(fund_code: str = "", mode: str = "mock"):
    return {"success": True, "data": query_service(mode).fund_nav(fund_code)}


@app.get("/api/fund/history")
def fund_history(fund_code: str = "", start_date: str = "", end_date: str = "", mode: str = "mock"):
    return {"success": True, "data": query_service(mode).fund_history(fund_code, start_date, end_date)}


@app.post("/api/watchlist")
def add_watchlist(payload: WatchlistRequest):
    return {"success": True, "data": service.add_watchlist(payload.item_type, payload.symbol, payload.name)}


@app.delete("/api/watchlist/{item_id}")
def delete_watchlist(item_id: str):
    return {"success": True, "data": service.delete_watchlist(item_id)}


@app.get("/api/watchlist")
def list_watchlist():
    return {"success": True, "data": service.list_watchlist()}


@app.post("/api/portfolio/holding")
def add_holding(payload: HoldingRequest):
    return {
        "success": True,
        "data": service.add_holding(
            payload.item_type,
            payload.symbol,
            payload.quantity,
            payload.cost_price,
            payload.name,
        ),
    }


@app.get("/api/portfolio/summary")
def portfolio_summary():
    return {"success": True, "data": service.portfolio_summary()}


@app.get("/api/risk/alerts")
def risk_alerts():
    return {"success": True, "data": service.risk_alerts()}
