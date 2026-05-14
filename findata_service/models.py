from pydantic import BaseModel, Field


class WatchlistRequest(BaseModel):
    item_type: str = Field(pattern="^(stock|fund|index)$")
    symbol: str
    name: str | None = None


class DbWatchlistRequest(WatchlistRequest):
    created_by: str = "tester"


class HoldingRequest(BaseModel):
    item_type: str = Field(pattern="^(stock|fund)$")
    symbol: str
    quantity: float = Field(gt=0)
    cost_price: float = Field(gt=0)
    name: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TestRunLogRequest(BaseModel):
    suite_name: str
    passed_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    duration_seconds: float = Field(ge=0)


class ApiResult(BaseModel):
    success: bool = True
    data: dict | list
