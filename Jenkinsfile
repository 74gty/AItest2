pipeline {
    agent any

    options {
        timestamps()
    }

    parameters {
        choice(
            name: 'TEST_SCOPE',
            choices: ['all-stable', 'findata-api', 'findata-db', 'findata-ui', 'findata-all'],
            description: '选择金融平台测试范围。默认 all-stable 不强制依赖浏览器。'
        )
        string(name: 'REMOTE_URL', defaultValue: 'http://host.docker.internal:4444/wd/hub', description: 'Selenium Remote WebDriver 地址')
        string(name: 'FINDATA_URL', defaultValue: 'http://host.docker.internal:8010', description: '金融平台 Web 地址')
    }

    environment {
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare') {
            steps {
                sh '''
                    set -e
                    find reports -mindepth 1 ! -name .gitkeep -delete 2>/dev/null || true
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install -U pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    set -e
                    . .venv/bin/activate

                    case "$TEST_SCOPE" in
                        all-stable)
                            pytest tests/test_config.py \
                                tests/test_findata_api.py \
                                tests/test_findata_service.py \
                                tests/test_findata_bulk_cases.py \
                                tests/test_findata_market_samples.py -v
                            ;;
                        findata-api)
                            pytest tests/test_findata_api.py tests/test_findata_db_api.py -v
                            ;;
                        findata-db)
                            pytest tests/test_findata_mysql.py tests/test_findata_db_api.py -v
                            ;;
                        findata-ui)
                            pytest tests/test_findata_ui.py -v --run-ui \
                                --remote-url "$REMOTE_URL" \
                                --findata-url "$FINDATA_URL"
                            ;;
                        findata-all)
                            pytest -m findata -v
                            ;;
                        *)
                            echo "Unsupported TEST_SCOPE: $TEST_SCOPE"
                            exit 2
                            ;;
                    esac
                '''
            }
        }

        stage('Allure Report') {
            steps {
                script {
                    catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                        allure includeProperties: false, jdk: '', results: [[path: 'reports']]
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}
