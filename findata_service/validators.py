from datetime import datetime

from findata_service.errors import FindataError


def validate_symbol(symbol, field_name="symbol"):
    if not symbol or not str(symbol).strip():
        raise FindataError("INVALID_SYMBOL", f"{field_name} 不能为空，请传入有效代码，例如 600519")
    return str(symbol).strip()


def validate_fund_code(fund_code):
    if not fund_code or not str(fund_code).isdigit() or len(str(fund_code)) != 6:
        raise FindataError("INVALID_FUND_CODE", "基金代码必须是 6 位数字")
    return str(fund_code)


def parse_date(value, field_name):
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except (TypeError, ValueError) as error:
        raise FindataError(
            "INVALID_DATE",
            f"{field_name} 必须使用 YYYYMMDD 格式",
            details={field_name: value},
        ) from error


def validate_date_range(start_date, end_date):
    start = parse_date(start_date, "start_date")
    end = parse_date(end_date, "end_date")
    if start > end:
        raise FindataError(
            "INVALID_DATE_RANGE",
            "start_date 不能晚于 end_date",
            details={"start_date": start_date, "end_date": end_date},
        )
    return start, end
