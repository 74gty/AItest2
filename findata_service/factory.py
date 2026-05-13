import os

from findata_service.data_sources import AkShareDataSource, BaoStockDataSource, MockDataSource, ResilientDataSource
from findata_service.errors import FindataError


def create_findata_source(mode=None):
    mode = mode or os.getenv("FINDATA_MODE", "mock")
    if mode == "live":
        try:
            return ResilientDataSource(AkShareDataSource(), fallback=BaoStockDataSource())
        except FindataError:
            # 本地或 CI 未安装真实数据源时回落到 Mock，保证服务仍可启动
            return ResilientDataSource(MockDataSource())
    return ResilientDataSource(MockDataSource())
