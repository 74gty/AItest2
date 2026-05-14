# EUTL 金融行情质量工程平台

EUTL 是一个围绕金融行情聚合场景建设的质量工程项目，覆盖后端接口、Web 仪表盘、MySQL 数据校验、自动化测试、Allure 报告与 Jenkins CI/CD 流水线。项目以金融行情查询、自选关注、模拟组合和风险提醒为业务主线，沉淀了接口自动化、UI 自动化、数据驱动、数据库断言和持续集成能力。

## 项目亮点

- 金融业务闭环：行情查询、自选关注、模拟持仓、组合汇总、风险提醒。
- 测试体系完整：接口测试、功能测试、UI 测试、数据库测试、数据驱动测试。
- 数据资产可复用：沉淀股票/基金样本库、批量接口用例、CRM 测试设计矩阵。
- CI/CD 可落地：Jenkins 参数化流水线按测试范围分组执行，并归档 Allure 结果。
- 工程结构清晰：FastAPI 服务、Page Object、数据库仓储层、pytest 用例分层组织。

## 技术栈

- Python / FastAPI / pytest
- Selenium Remote WebDriver
- MySQL / PyMySQL
- Allure Report
- Jenkins Pipeline
- Docker Selenium Chrome

## 核心能力

| 能力 | 说明 |
|---|---|
| 接口测试 | 覆盖金融行情、登录、自选关注、组合汇总、风险提醒、数据库演示接口 |
| UI 测试 | 基于 Selenium + Page Object 覆盖登录、仪表盘、行情查询、自选关注 |
| 数据库测试 | MySQL 建表、写入、查询、删除、测试执行日志、接口数据落库校验 |
| 数据驱动 | CSV 批量用例覆盖股票、基金、指数、日期范围和异常参数 |
| 测试设计 | CRM 业务域沉淀 218 条测试设计矩阵，核心模块覆盖率 96%+ |
| CI/CD | Jenkins 支持稳定回归、接口、数据库、UI、金融全量分组执行 |

## 目录结构

```text
config/                 # 环境配置模板
database/               # MySQL 连接、建表、仓储操作
findata_service/        # 金融平台后端、页面模板和静态资源
pages/                  # Selenium Page Object
tests/                  # 金融平台自动化测试
tests/data/             # 金融样本库和数据驱动用例
automation-scripts/     # CRM 测试设计与自动化示例
reports/.gitkeep        # Allure 结果目录占位
Jenkinsfile             # Jenkins CI/CD 流水线
```

## 快速启动

安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

启动金融服务：

```bash
scripts/start_findata.sh 8010 0.0.0.0
```

访问入口：

```text
Web 仪表盘：http://localhost:8010/login
接口文档：http://localhost:8010/docs
接口说明：http://localhost:8010/api
健康检查：http://localhost:8010/api/health
```

停止服务：

```bash
scripts/stop_findata.sh 8010
```

## 数据库能力

MySQL 连接信息通过 `config/config.yaml` 或环境变量维护。数据库模块提供可重复执行的初始化脚本和仓储层封装，适合在本地、Jenkins 或容器化环境中进行数据准备和断言。

初始化表结构：

```bash
curl -X POST http://localhost:8010/api/db/init
```

写入数据库自选：

```bash
curl -X POST http://localhost:8010/api/db/watchlist \
  -H "Content-Type: application/json" \
  -d '{"item_type":"stock","symbol":"600519","name":"贵州茅台","created_by":"tester"}'
```

查询数据库自选：

```bash
curl "http://localhost:8010/api/db/watchlist?created_by=tester"
```

## 自动化测试

稳定回归：

```bash
./.venv/bin/python -m pytest -q
```

金融接口测试：

```bash
./.venv/bin/python -m pytest tests/test_findata_api.py tests/test_findata_db_api.py -v
```

金融业务和数据驱动测试：

```bash
./.venv/bin/python -m pytest \
  tests/test_findata_service.py \
  tests/test_findata_bulk_cases.py \
  tests/test_findata_market_samples.py -v
```

MySQL 数据库测试：

```bash
./.venv/bin/python -m pytest tests/test_findata_mysql.py tests/test_findata_db_api.py -v
```

金融 UI 测试：

```bash
docker start selenium-chrome
scripts/start_findata.sh 8010 0.0.0.0
./.venv/bin/python -m pytest tests/test_findata_ui.py -v --run-ui \
  --remote-url http://localhost:4444/wd/hub \
  --findata-url http://host.docker.internal:8010
```

CRM 测试设计资产校验：

```bash
./.venv/bin/python -m pytest automation-scripts/suitecrm/tests/test_suitecrm_test_design.py -v
```

## Jenkins CI/CD

流水线文件：`Jenkinsfile`

支持的 `TEST_SCOPE`：

```text
all-stable   稳定回归
findata-api  金融接口测试
findata-db   金融数据库测试
findata-ui   金融 UI 测试
findata-all  金融模块全量测试
```

推荐参数：

```text
REMOTE_URL=http://host.docker.internal:4444/wd/hub
FINDATA_URL=http://host.docker.internal:8010
```

## 测试资产

```text
tests/data/findata_bulk_cases.csv
tests/data/findata_market_samples.csv
automation-scripts/suitecrm/test_design/suitecrm_test_case_matrix.csv
automation-scripts/suitecrm/test_design/suitecrm_xmind_outline.txt
```

这些文件用于展示数据驱动测试、样本覆盖、测试点拆解和用例设计能力。运行产物、虚拟环境、个人记录和本地缓存不进入仓库。
