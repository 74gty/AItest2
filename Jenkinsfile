pipeline {
    agent any

    options {
        timestamps()
    }

    parameters {
        choice(
            name: 'TEST_SCOPE',
            choices: ['all-stable', 'findata', 'gitea-ui', 'suitecrm-ui', 'suitecrm-api'],
            description: '选择本次流水线要执行的测试范围。默认 all-stable 不依赖外部账号和浏览器，会跳过需手动启用的 UI/API 用例。'
        )
        string(name: 'REMOTE_URL', defaultValue: 'http://host.docker.internal:4444/wd/hub', description: 'Selenium Remote WebDriver 地址')
        string(name: 'GITEA_URL', defaultValue: 'http://host.docker.internal:3000', description: 'Gitea 被测服务地址')
        string(name: 'SUITECRM_URL', defaultValue: 'http://host.docker.internal:8081', description: 'SuiteCRM Web 地址')
        string(name: 'SUITECRM_API_URL', defaultValue: 'http://host.docker.internal:8081/Api', description: 'SuiteCRM API 地址')
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
                            pytest -v
                            ;;
                        findata)
                            pytest -m findata -v
                            ;;
                        gitea-ui)
                            pytest tests/test_gitea.py -v --run-ui \
                                --remote-url "$REMOTE_URL" \
                                --gitea-url "$GITEA_URL"
                            ;;
                        suitecrm-ui)
                            pytest automation-scripts/suitecrm/tests -v --run-suitecrm-ui \
                                --remote-url "$REMOTE_URL" \
                                --suitecrm-url "$SUITECRM_URL"
                            ;;
                        suitecrm-api)
                            pytest automation-scripts/suitecrm/tests -v --run-suitecrm-api \
                                --suitecrm-api-url "$SUITECRM_API_URL"
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
