pipeline {
    agent any

    environment {
        PROJECT_DIR = "/workspace/selenium"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        REMOTE_URL = "http://host.docker.internal:4444/wd/hub"
        GITEA_URL = "http://host.docker.internal:3000"
    }

    stages {
        stage('Prepare') {
            steps {
                dir("${PROJECT_DIR}") {
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
        }

        stage('Run Tests') {
            steps {
                dir("${PROJECT_DIR}") {
                    sh '''
                        set -e
                        . .venv/bin/activate
                        pytest -v --run-ui \
                            --remote-url "$REMOTE_URL" \
                            --gitea-url "$GITEA_URL"
                    '''
                }
            }
        }

        stage('Allure Report') {
            steps {
                dir("${PROJECT_DIR}") {
                    allure includeProperties: false, jdk: '', results: [[path: 'reports']]
                }
            }
        }
    }

    post {
        always {
            dir("${PROJECT_DIR}") {
                archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            }
        }
    }
}
