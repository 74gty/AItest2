from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from database import repository
from database.schema import init_database
from findata_service.auth import SESSION_COOKIE, authenticate, findata_auth_config, is_authenticated
from findata_service.errors import FindataError, error_response
from findata_service.factory import create_findata_source
from findata_service.models import DbWatchlistRequest, HoldingRequest, LoginRequest, TestRunLogRequest, WatchlistRequest
from findata_service.service import FindataService


app = FastAPI(title="EUTL 金融行情数据聚合与风险监控测试平台")
service = FindataService(data_source=create_findata_source())
BASE_DIR = Path(__file__).resolve().parent
INDEX_TEMPLATE = BASE_DIR / "templates" / "index.html"
LOGIN_TEMPLATE = BASE_DIR / "templates" / "login.html"
DASHBOARD_TEMPLATE = BASE_DIR / "templates" / "dashboard.html"
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def query_service(mode: str = "mock"):
    # mode 只影响本次查询，避免网页体验真实数据时破坏 CI 默认 Mock 稳定性
    if mode == "live":
        return FindataService(data_source=create_findata_source("live"))
    return service


@app.exception_handler(FindataError)
def handle_findata_error(request: Request, error: FindataError):
    return JSONResponse(status_code=error.status_code, content=error_response(error))


@app.get("/")
def root(request: Request):
    # 根路径按登录状态分流，保留 /api 和 /docs 作为接口测试入口
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@app.get("/api")
def api_index():
    # 旧版接口说明页挪到 /api，避免和登录后的首页冲突
    return HTMLResponse(INDEX_TEMPLATE.read_text(encoding="utf-8"))


@app.get("/login")
def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard", status_code=302)
    return HTMLResponse(LOGIN_TEMPLATE.read_text(encoding="utf-8"))


@app.get("/dashboard")
def dashboard_page(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)
    return HTMLResponse(DASHBOARD_TEMPLATE.read_text(encoding="utf-8"))


@app.post("/api/auth/login")
def login(payload: LoginRequest):
    if not authenticate(payload.username, payload.password):
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": {"code": "INVALID_LOGIN", "message": "用户名或密码错误"}},
        )

    response = JSONResponse(content={"success": True, "data": {"username": payload.username}})
    response.set_cookie(
        key=SESSION_COOKIE,
        value=findata_auth_config()["session_token"],
        httponly=True,
        samesite="lax",
    )
    return response


@app.post("/api/auth/logout")
def logout():
    response = JSONResponse(content={"success": True, "data": {"logged_out": True}})
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/api/health")
def health():
    return {"success": True, "data": service.health()}


@app.post("/api/db/init")
def init_db():
    # 数据库初始化接口用于本地演示和自动化测试准备
    init_database()
    return {"success": True, "data": {"initialized": True}}


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


@app.post("/api/db/watchlist")
def add_db_watchlist(payload: DbWatchlistRequest):
    init_database()
    item = repository.add_watchlist_item(payload.item_type, payload.symbol, payload.name or payload.symbol, payload.created_by)
    return {"success": True, "data": item}


@app.get("/api/db/watchlist")
def list_db_watchlist(created_by: str | None = None):
    init_database()
    return {"success": True, "data": repository.list_watchlist_items(created_by)}


@app.delete("/api/db/watchlist/{item_id}")
def delete_db_watchlist(item_id: int):
    init_database()
    item = repository.delete_watchlist_item(item_id)
    if not item:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"code": "DB_WATCHLIST_NOT_FOUND", "message": "数据库自选关注不存在"}},
        )
    return {"success": True, "data": item}


@app.post("/api/db/test-run-logs")
def add_db_test_run_log(payload: TestRunLogRequest):
    init_database()
    log = repository.add_test_run_log(
        payload.suite_name,
        payload.passed_count,
        payload.failed_count,
        payload.duration_seconds,
    )
    return {"success": True, "data": log}


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
