# EUTL 金融行情数据聚合与风险监控测试平台

本文档面向仓库读者，说明金融模块的业务定位、数据来源、测试方式和 CI/CD 使用方式。它与主 README 不冲突，主 README 保持项目总览，本文件聚焦金融行情模块。

## 模块定位

`findata_service` 是 EUTL 中的金融行情测试子平台，用于验证股票、基金、指数、交易日历、自选关注、模拟组合、风险提醒、缓存降级和接口自动化测试能力。

本模块只使用公开金融行情数据，不涉及真实交易、下单、证券账户、资金划转或投资建议。

## 数据模式

默认模式是 `mock`，用于本地回归、Jenkins 构建和 Allure 报告生成。Mock 数据稳定、可重复，适合自动化测试。

真实数据模式是 `live`，用于人工体验或抽样验证。`live` 优先调用 AKShare，失败后尝试缓存和 BaoStock 备用能力。真实数据依赖网络和免费数据源稳定性，不建议作为 CI/CD 的强制门禁。

## 样本库

金融样本库文件：

```text
tests/data/findata_market_samples.csv
```

当前样本库包含 280 条样本：

- 股票样本：180 条
- 基金样本：100 条

样本库用于：

- 校验股票/基金代码格式
- 保证测试数据覆盖面
- 支撑批量自动化脚本
- 为后续真实数据抽样测试提供候选池

样本库不是交易推荐清单，只是测试数据资产。

## 数据来源口径

股票样本参考 AKShare 沪深京 A 股实时行情接口口径。AKShare 文档说明 `stock_zh_a_spot_em` 面向东方财富沪深京 A 股实时行情数据，并返回代码、名称、最新价、涨跌幅等字段。

基金样本参考 AKShare 公募基金基本信息接口口径。AKShare 文档说明 `fund_name_em` 面向东方财富/天天基金的所有基金基本信息数据，并返回基金代码、基金简称、基金类型等字段。

交易所参考入口：

- 上海证券交易所股票列表：https://www.sse.com.cn/assortment/stock/list/share/
- 深圳证券交易所股票列表：https://www.szse.cn/market/product/stock/list/index.html

AKShare 文档入口：

- 股票数据：https://akshare.akfamily.xyz/data/stock/stock.html
- 公募基金数据：https://akshare.akfamily.xyz/data/fund/fund_public.html

## 本地运行

启动服务：

```bash
scripts/start_findata.sh 8010
```

停止服务：

```bash
scripts/stop_findata.sh 8010
```

浏览器入口：

```text
http://localhost:8010/
```

Swagger 接口文档：

```text
http://localhost:8010/docs
```

## 常用测试命令

运行金融核心回归测试：

```bash
./.venv/bin/python -m pytest tests/test_findata_service.py -v
```

运行数据驱动接口用例：

```bash
./.venv/bin/python -m pytest tests/test_findata_bulk_cases.py -v
```

运行 200+ 样本库质量校验：

```bash
./.venv/bin/python -m pytest tests/test_findata_market_samples.py -v
```

运行金融模块全部测试：

```bash
./.venv/bin/python -m pytest -m findata -v
```

## CI/CD 关系

金融模块已经接入 pytest 统一测试体系。Jenkins 执行项目测试时，会自动发现 `tests/` 下的金融测试，并把结果写入 `reports/`，再由 Allure 生成报告。

CI/CD 默认使用 Mock 数据，不需要真实金融网站稳定在线，也不需要账号注册。这保证了构建结果可重复、可追踪。

## 扩展建议

如果要做几百条甚至上千条测试，不建议写几百个 Python 测试文件。推荐继续扩展 CSV 数据文件，然后用 pytest 参数化测试读取数据。

推荐分层：

- `findata_bulk_cases.csv`：少量强断言接口用例，适合作为 CI 门禁
- `findata_market_samples.csv`：大规模股票/基金样本库，适合数据质量校验和抽样测试
- 后续新增 `findata_live_sample_cases.csv`：真实数据抽样用例，默认跳过，只在人工或定时任务中开启
