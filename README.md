# EUTL 金融行情测试平台

EUTL 是一个面向软件测试开发练习的金融行情测试平台，重点展示后端接口、轻量前端、MySQL 数据库、pytest 自动化、Selenium UI 测试、Allure 报告和 Jenkins CI/CD 基础流程。

项目默认使用 Mock 金融数据，适合本地演示和 CI 回归；真实数据源入口保留在 AKShare/BaoStock 适配层中。平台仅用于测试实践，不涉及真实交易、下单、证券账户或资金划转。

## 功能范围

- FastAPI 金融接口：股票、基金、指数、交易日历、自选关注、模拟持仓、组合汇总、风险提醒。
- Web 页面：登录页和仪表盘，支持行情查询、自选关注、模拟组合、风险提醒、数据库自选。
- MySQL 示例：建表、增删改查、接口写入、数据库断言、测试执行日志。
- 自动化测试：接口测试、功能测试、数据驱动测试、数据库测试、Selenium UI 测试。
- CI/CD：Jenkins 参数化流水线，支持稳定回归、接口、数据库、UI 分组执行。

## 技术栈

- Python 3
- FastAPI
- pytest
- Selenium Remote WebDriver
- MySQL + PyMySQL
- Allure
- Jenkins Pipeline

## 目录结构

```text
config/                 # 本地测试配置
database/               # MySQL 连接、建表和仓储操作
findata_service/        # 金融平台后端、页面模板和静态资源
pages/                  # Selenium Page Object
tests/                  # pytest 自动化测试
tests/data/             # 可提交的样本数据和数据驱动用例
reports/.gitkeep        # Allure 结果目录占位
Jenkinsfile             # CI/CD 流水线
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

浏览器访问：

```text
http://localhost:8010/login
```

默认演示账号：

```text
tester / tester123
```

常用入口：

```text
登录页：http://localhost:8010/login
接口文档：http://localhost:8010/docs
接口说明：http://localhost:8010/api
健康检查：http://localhost:8010/api/health
```

停止服务：

```bash
scripts/stop_findata.sh 8010
```

## MySQL 配置

默认数据库配置位于 `config/config.yaml`：

```yaml
mysql_host: "127.0.0.1"
mysql_port: 3306
mysql_user: "eutl"
mysql_password: "eutl123456"
mysql_database: "eutl_test"
```

WSL2 本地启动 MySQL：

```bash
sudo service mysql start
```

初始化数据库表：

```bash
curl -X POST http://localhost:8010/api/db/init
```

写入一条数据库自选：

```bash
curl -X POST http://localhost:8010/api/db/watchlist \
  -H "Content-Type: application/json" \
  -d '{"item_type":"stock","symbol":"600519","name":"贵州茅台","created_by":"tester"}'
```

查询数据库自选：

```bash
curl "http://localhost:8010/api/db/watchlist?created_by=tester"
```

也可以直接进入 MySQL 查询：

```bash
mysql -u eutl -p eutl_test
```

```sql
SELECT item_id, item_type, symbol, name, created_by, created_at
FROM findata_watchlist
ORDER BY item_id DESC;
```

## 自动化测试

运行稳定回归：

```bash
./.venv/bin/python -m pytest -q
```

运行金融 HTTP 接口测试：

```bash
./.venv/bin/python -m pytest tests/test_findata_api.py tests/test_findata_db_api.py -v
```

运行金融业务和数据驱动测试：

```bash
./.venv/bin/python -m pytest \
  tests/test_findata_service.py \
  tests/test_findata_bulk_cases.py \
  tests/test_findata_market_samples.py -v
```

运行 MySQL 数据库测试：

```bash
sudo service mysql start
./.venv/bin/python -m pytest tests/test_findata_mysql.py tests/test_findata_db_api.py -v
```

运行金融 UI 测试：

```bash
docker start selenium-chrome
scripts/start_findata.sh 8010 0.0.0.0
./.venv/bin/python -m pytest tests/test_findata_ui.py -v --run-ui \
  --remote-url http://localhost:4444/wd/hub \
  --findata-url http://host.docker.internal:8010
```

## Jenkins CI/CD

流水线文件：`Jenkinsfile`

支持的 `TEST_SCOPE`：

```text
all-stable   稳定回归，不强制依赖浏览器
findata-api  金融 HTTP 接口测试
findata-db   金融 MySQL 数据库测试
findata-ui   金融 Selenium UI 测试
findata-all  金融模块完整测试
```

Jenkins 中建议配置：

```text
REMOTE_URL=http://host.docker.internal:4444/wd/hub
FINDATA_URL=http://host.docker.internal:8010
```

UI 测试需要 Jenkins 能访问 Selenium Chrome 和金融服务。数据库测试需要 Jenkins 运行环境能连接 `config/config.yaml` 中配置的 MySQL。

## 可提交数据

仓库保留少量可公开的测试样本，方便其他人拉取后直接看到项目可用：

```text
tests/data/findata_bulk_cases.csv
tests/data/findata_market_samples.csv
```

不会上传的本地内容包括虚拟环境、Allure 运行结果、个人记录、缓存文件和本地工具目录，规则见 `.gitignore`。
