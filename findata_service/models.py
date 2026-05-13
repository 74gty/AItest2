from pydantic import BaseModel, Field


class WatchlistRequest(BaseModel):
    item_type: str = Field(pattern="^(stock|fund|index)$")
    symbol: str
    name: str | None = None


class HoldingRequest(BaseModel):
    item_type: str = Field(pattern="^(stock|fund)$")
    symbol: str
    quantity: float = Field(gt=0)
    cost_price: float = Field(gt=0)
    name: str | None = None


class ApiResult(BaseModel):
    success: bool = True
    data: dict | list
