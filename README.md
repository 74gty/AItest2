# Enterprise Unified Test Lab (EUTL)

面向企业级测试实践的自动化测试平台示例，覆盖 UI 自动化、API 自动化、数据驱动测试、Allure 报告与 Jenkins CI/CD。

当前项目作为 EUTL 的基地框架，逐步融合代码托管服务、企业 CRM 与金融行情数据聚合测试能力。

当前重点模块：EUTL 金融行情数据聚合与风险监控测试平台，基于 AKShare/BaoStock 的公开金融数据能力，支持股票/基金行情查询、自选关注、模拟组合、风险提醒、缓存降级和接口自动化测试。

## 运行环境

- Python 3.14.4（当前 WSL 虚拟环境）
- Selenium
- Docker Chrome 容器

## VS Code 配置

项目已配置默认解释器：

```text
${workspaceFolder}/.venv/bin/python
```

## 目录结构

```text
config/        # 测试配置：Gitea 地址、账号、Selenium Remote 地址
pages/         # 页面对象：只写页面元素和页面操作
tests/         # 测试用例：只写测试步骤和断言
utils/         # 工具函数：配置读取等公共能力
reports/       # Allure 报告结果
findata_service/
  # EUTL 金融行情数据聚合与风险监控测试平台
automation-scripts/
  suitecrm/    # SuiteCRM UI + API 自动化测试框架
```

核心流程：

```text
pytest 用例 -> Page Object 页面操作 -> Selenium Remote -> Docker Chrome -> Gitea Web
```

## 运行方式

启动 Docker Chrome：

```bash
docker run -d --name selenium-chrome -p 4444:4444 -p 7900:7900 --shm-size=2g selenium/standalone-chrome:latest
```

启动 Gitea 被测服务：

```bash
docker pull gitea/gitea:latest
docker run -d --name gitea -p 3000:3000 -p 222:22 gitea/gitea:latest
```

启动后访问：

```text
http://localhost:3000
```

如果是首次启动 Gitea，请先在浏览器里完成初始化并创建测试账号。

运行基础框架测试：

```bash
./.venv/bin/python -m pytest -v
```

运行需要 Docker Chrome 的 UI 测试：

```bash
./.venv/bin/python -m pytest -v --run-ui
```

运行 Gitea 登录测试：

```bash
./.venv/bin/python -m pytest tests/test_gitea.py -v --run-ui --gitea-username your-user --gitea-password your-password
```

运行百度搜索脚本：

```bash
./.venv/bin/python test_selenium_baidu.py
```

脚本会通过 Docker Chrome 打开百度首页，搜索关键词，并将截图保存为 `result.png`。

查看 Allure 报告：

```bash
allure serve reports
```

如果终端提示 `Browse operation is not supported`，不是报错，手动打开终端里显示的地址即可。

如果提示 `allure: command not found`，先确认已激活虚拟环境：

```bash
source .venv/bin/activate
allure --version
```

当前项目已在 `.venv/bin/allure` 配好本地 Allure 命令，依赖放在 `.tools/`，不需要全局安装。

## Jenkins 自动化执行

启动 Jenkins。推荐镜像中预装 Python、Git、Allure 插件；如果使用自定义镜像，确保容器内可以执行 `python3`、`git` 和 `pip`：

```bash
docker pull jenkins/jenkins:lts
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 --add-host=host.docker.internal:host-gateway -v jenkins_home:/var/jenkins_home jenkins-python:local
```

查看初始管理员密码：

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

访问：

```text
http://localhost:8080
```

初始化后安装建议插件，并确保安装 Pipeline、Git、Allure 相关插件。

创建一键自动化流水线：

```text
New Item
输入任务名，例如 eutl-ci
选择 Pipeline
Pipeline 区域选择 Pipeline script from SCM
SCM 选择 Git
Repository URL 填写仓库地址，例如：
  GitHub: https://github.com/74gty/AItest2.git
  Gitee: git@gitee.com:jkiyi/ai-test-1.git
Branch Specifier 填写 */main
Script Path 填写 Jenkinsfile
Save
Build Now
```

流水线默认参数 `TEST_SCOPE=all-stable`，点击 `Build Now` 就会自动完成：

```text
拉取仓库代码
创建 Python 虚拟环境
安装 requirements.txt
运行 pytest 稳定回归
生成 reports/ Allure 原始结果
归档 reports/**
```

可选测试范围：

```text
all-stable   默认稳定回归，不强依赖浏览器、Gitea、SuiteCRM 账号
findata      只运行 EUTL 金融行情数据聚合与风险监控测试平台
gitea-ui     运行 Gitea UI 测试，需要 Selenium Chrome 与 Gitea 服务
suitecrm-ui  运行 SuiteCRM UI 测试，需要 Selenium Chrome 与 SuiteCRM Web
suitecrm-api 运行 SuiteCRM API 测试，需要 SuiteCRM API 与 OAuth 配置
```

Jenkins 容器内访问宿主机端口时使用 `host.docker.internal`，所以 UI 测试参数默认会连接：

```text
http://host.docker.internal:4444/wd/hub
http://host.docker.internal:3000
```

## EUTL 阶段 1：SuiteCRM 测试框架

SuiteCRM 作为企业 CRM 业务域，第一阶段优先覆盖：

- 登录/权限
- 客户（Contacts）与公司账户（Accounts）
- 销售线索（Leads）与机会（Opportunities）
- 活动与任务（Activities / Calendar）

当前已建立 SuiteCRM 独立自动化目录：

```text
automation-scripts/suitecrm/
  api/          # Requests + Pytest 的 API Client、Schema、校验工具
  ui/pages/     # SuiteCRM Page Object
  tests/        # SuiteCRM UI/API 测试用例
```

默认运行 `pytest` 时，SuiteCRM 外部依赖用例会跳过，不影响现有 Gitea 和基础框架测试。

运行 SuiteCRM UI 测试：

```bash
./.venv/bin/python -m pytest automation-scripts/suitecrm/tests -v --run-suitecrm-ui \
  --suitecrm-url http://host.docker.internal:8081 \
  --suitecrm-username your-user \
  --suitecrm-password 'your-password'
```

运行 SuiteCRM API 测试：

```bash
./.venv/bin/python -m pytest automation-scripts/suitecrm/tests -v --run-suitecrm-api \
  --suitecrm-api-url http://localhost:8081/Api \
  --suitecrm-username your-user \
  --suitecrm-password 'your-password' \
  --suitecrm-client-id your-client-id \
  --suitecrm-client-secret your-client-secret
```

如果 SuiteCRM 运行在 Docker 容器中，并且测试从另一个容器访问宿主机端口，请将 `localhost` 替换为 `host.docker.internal`。

## EUTL 阶段 2：金融行情数据聚合与风险监控测试平台

`findata_service` 是 EUTL 金融行情数据聚合与风险监控测试平台的服务模块，面向公开金融行情查询、模拟组合和风险监控测试场景，不涉及真实交易、下单、证券账户或资金划转。

当前第一版已建立：

- FastAPI 服务骨架
- Mock 数据模式，默认用于自动化测试和 CI/CD
- AKShare 主数据源适配入口
- BaoStock 历史行情备用数据源适配入口
- 内存缓存与数据源降级结构：主源失败时优先读缓存，缓存缺失时尝试备用源
- 股票行情、历史 K 线、指数行情、交易日历接口
- 基金基本信息、净值、历史净值接口
- 自选关注、模拟持仓、组合汇总、风险提醒接口
- 统一业务错误结构

服务目录：

```text
findata_service/
  app.py          # FastAPI 路由入口
  templates/      # 中文首页说明，可直接修改 index.html
  service.py      # 自选、组合、风险等业务逻辑
  factory.py      # Mock/真实数据源模式选择
  data_sources.py # Mock / AKShare / BaoStock 数据源适配
  cache.py        # 内存缓存
  validators.py   # 参数校验
```

安装依赖：

```bash
./.venv/bin/python -m pip install -r requirements.txt
```

启动服务：

```bash
scripts/start_findata.sh 8010
```

停止服务：

```bash
scripts/stop_findata.sh 8010
```

访问健康检查：

```bash
curl http://localhost:8010/api/health
```

示例接口：

```bash
curl "http://localhost:8010/api/stock/realtime?symbol=600519"
curl "http://localhost:8010/api/stock/history?symbol=600519&start_date=20240101&end_date=20241231"
curl "http://localhost:8010/api/index/history?symbol=sh000300&start_date=20240101&end_date=20241231"
curl "http://localhost:8010/api/fund/basic?fund_code=000001"
curl "http://localhost:8010/api/fund/nav?fund_code=000001"
curl "http://localhost:8010/api/fund/history?fund_code=000001&start_date=20240101&end_date=20241231"
```

中文首页说明文件：

```text
findata_service/templates/index.html
```

如果只是想改首页里“字段说明”“Try it out 是什么”“示例参数”等中文文案，直接改这个文件即可。

运行当前 Mock 回归测试：

```bash
./.venv/bin/python -m pytest tests/test_findata_service.py -v
```

运行批量数据驱动测试：

```bash
./.venv/bin/python -m pytest tests/test_findata_bulk_cases.py -v
```

批量测试数据文件：

```text
tests/data/findata_bulk_cases.csv
```

如果要扩展到几百条用例，不需要写几百个测试脚本，只需要在 CSV 里继续增加行；pytest 会把每一行当成一条自动化用例执行。

金融样本库文件：

```text
tests/data/findata_market_samples.csv
```

样本库当前包含股票和基金样本，用于批量测试数据准备、代码格式校验、覆盖面校验和后续真实数据抽样测试。

运行样本库质量校验：

```bash
./.venv/bin/python -m pytest tests/test_findata_market_samples.py -v
```

后续接入真实数据时，AKShare 作为主数据源，BaoStock 作为 A 股历史行情和基础信息备用数据源；CI/CD 默认继续使用 Mock 模式，保证回归稳定。

如需尝试真实数据源模式：

```bash
http://localhost:8010/api/stock/realtime?symbol=600519&mode=live
```

真实模式依赖免费数据源网络稳定性；上传仓库和 CI 回归建议继续使用默认 Mock 模式。
