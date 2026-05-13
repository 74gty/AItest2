import csv
import re
from collections import Counter
from pathlib import Path

import pytest


pytestmark = pytest.mark.findata

SAMPLE_FILE = Path(__file__).resolve().parent / "data" / "findata_market_samples.csv"
STOCK_CODE = re.compile(r"^\d{6}$")
FUND_CODE = re.compile(r"^\d{6}$")


def load_samples():
    with SAMPLE_FILE.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def test_market_sample_dataset_is_large_enough():
    rows = load_samples()
    counts = Counter(row["asset_type"] for row in rows)

    assert len(rows) >= 200
    assert counts["stock"] >= 100
    assert counts["fund"] >= 80


def test_market_sample_dataset_has_unique_ids_and_symbols():
    rows = load_samples()
    sample_ids = [row["sample_id"] for row in rows]
    typed_symbols = [(row["asset_type"], row["symbol"]) for row in rows]

    assert len(sample_ids) == len(set(sample_ids))
    assert len(typed_symbols) == len(set(typed_symbols))


@pytest.mark.parametrize("row", load_samples(), ids=lambda item: item["sample_id"])
def test_market_sample_dataset_schema(row):
    assert row["asset_type"] in {"stock", "fund"}
    assert row["name"]
    assert row["preferred_endpoint"] in {"stock_realtime", "fund_nav"}

    if row["asset_type"] == "stock":
        assert STOCK_CODE.match(row["symbol"])
        assert row["preferred_endpoint"] == "stock_realtime"
    if row["asset_type"] == "fund":
        assert FUND_CODE.match(row["symbol"])
        assert row["preferred_endpoint"] == "fund_nav"
