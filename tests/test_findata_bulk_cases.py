import csv
from pathlib import Path

import pytest

from findata_service.errors import FindataError
from findata_service.service import FindataService


pytestmark = pytest.mark.findata

CASE_FILE = Path(__file__).resolve().parent / "data" / "findata_bulk_cases.csv"


def load_cases():
    with CASE_FILE.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


@pytest.mark.parametrize("case", load_cases(), ids=lambda item: item["case_id"])
def test_findata_bulk_cases(case):
    service = FindataService()

    try:
        result = call_operation(service, case)
    except FindataError as error:
        assert case["expected_success"] == "false"
        assert error.code == case["expected_code"]
        return

    assert case["expected_success"] == "true"
    assert result


def call_operation(service, case):
    operation = case["operation"]
    symbol = case["symbol"]
    start_date = case["start_date"]
    end_date = case["end_date"]

    if operation == "stock_realtime":
        return service.stock_realtime(symbol)
    if operation == "stock_history":
        return service.stock_history(symbol, start_date, end_date)
    if operation == "index_history":
        return service.index_history(symbol, start_date, end_date)
    if operation == "fund_basic":
        return service.fund_basic(symbol)
    if operation == "fund_nav":
        return service.fund_nav(symbol)
    if operation == "fund_history":
        return service.fund_history(symbol, start_date, end_date)

    raise AssertionError(f"未支持的批量测试操作：{operation}")
