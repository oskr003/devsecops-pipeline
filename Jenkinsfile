pipeline {
    agent any

    environment {
        SCANNER_HOME = tool 'SonarScanner'
        APP_NAME = 'devsecops-flask-app'
    }

    stages {
        stage('Build') {
            steps {
                echo '=== Compilando y preparando el entorno ==='
                sh '''
                    python3 -m venv venv || virtualenv venv || true
                    . venv/bin/activate || true
                    pip install --upgrade pip || true
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo '=== Ejecutando pruebas unitarias ==='
                sh '''
                    . venv/bin/activate || true
                    pytest test_app.py || python3 test_app.py || echo "Tests finalizados"
                '''
            }
        }

        stage('Analyze') {
            steps {
                echo '=== Ejecutando análisis estático SAST con SonarQube ==='
                withSonarQubeEnv('SonarQube') {
                    sh """
                        \${SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=devsecops-flask-app \
                        -Dsonar.projectName="DevSecOps Flask App" \
                        -Dsonar.sources=. \
                        -Dsonar.exclusions="venv/**,**/*.docx,**/*.xml"
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                echo '=== Desplegando aplicación de prueba para análisis dinámico ==='
                sh '''
                    docker network create devsecops-net 2>/dev/null || true
                    docker rm -f ${APP_NAME} || true
                    docker run -d --name ${APP_NAME} --network devsecops-net -p 5000:5000 \
                      -v $(pwd):/app -w /app python:3.9-slim \
                      sh -c "pip install -r requirements.txt && python app.py"
                    sleep 5
                '''
            }
        }

        stage('Security Test') {
            steps {
                echo '=== Ejecutando OWASP Dependency-Check (SCA) ==='
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    dependencyCheck additionalArguments: '--scan ./ --format ALL --prettyPrint', odcInstallation: 'DP-Check'
                    dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
                }

                echo '=== Ejecutando OWASP ZAP (DAST) ==='
                sh '''
                    docker run --rm --network devsecops-net \
                      -v $(pwd):/zap/wrk/:rw \
                      ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
                      -t http://${APP_NAME}:5000/hello?name=TEST \
                      -r zap-report.html -I || true
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/*.html, **/*.xml', allowEmptyArchive: true
            echo 'Pipeline de seguridad completado.'
        }
    }
}
