pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'arunkumarravi08'
        FRONTEND_IMAGE = "${DOCKER_REGISTRY}/login-frontend"
        BACKEND_IMAGE = "${DOCKER_REGISTRY}/login-backend"
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
        SONAR_PROJECT_KEY = 'login-page-project'
    }

    stages {
        stage('Git Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing global or pipeline dependencies if any...'
                // Generic step for global dependencies
            }
        }

        stage('Install Frontend Deps') {
            steps {
                dir('frontend') {
                    echo 'Installing Frontend dependencies...'
                    sh 'npm install'
                }
            }
        }

        stage('Install Backend Deps') {
            steps {
                dir('backend') {
                    echo 'Installing Backend dependencies...'
                    sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('ESLint') {
            steps {
                dir('frontend') {
                    echo 'Running ESLint...'
                    sh 'npm run lint'
                }
            }
        }

        stage('Tests') {
            steps {
                echo 'Starting tests execution phase...'
            }
        }

        stage('Frontend Tests') {
            steps {
                dir('frontend') {
                    echo 'Running Frontend Tests...'
                    sh 'npm test'
                }
            }
        }

        stage('Backend Tests') {
            steps {
                dir('backend') {
                    echo 'Running Backend Tests...'
                    sh '''
                    . venv/bin/activate
                    pytest test_app.py
                    '''
                }
            }
        }

        stage('SonarQube Scan') {
            steps {
                echo 'Running SonarQube Analysis...'
                withSonarQubeEnv('SonarQube') {
                    sh """
                    sonar-scanner \
                      -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                      -Dsonar.sources=frontend/src,backend \
                      -Dsonar.host.url=http://sonarqube:9000 \
                      -Dsonar.login=\$SONAR_AUTH_TOKEN
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                echo 'Checking Quality Gate...'
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Trivy FS Scan') {
            steps {
                echo 'Running Trivy FS Scan...'
                sh 'trivy fs --severity HIGH,CRITICAL .'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker images...'
                dir('frontend') {
                    sh "docker build -t ${FRONTEND_IMAGE}:${env.BUILD_ID} ."
                }
                dir('backend') {
                    sh "docker build -t ${BACKEND_IMAGE}:${env.BUILD_ID} ."
                }
            }
        }

        stage('Trivy Image Scan') {
            steps {
                echo 'Scanning Docker images with Trivy...'
                sh "trivy image --severity HIGH,CRITICAL ${FRONTEND_IMAGE}:${env.BUILD_ID}"
                sh "trivy image --severity HIGH,CRITICAL ${BACKEND_IMAGE}:${env.BUILD_ID}"
            }
        }

        stage('Docker Login') {
            steps {
                echo 'Logging into Docker Registry...'
                withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'
                }
            }
        }

        stage('Docker Push') {
            steps {
                echo 'Pushing Docker images...'
                sh "docker push ${FRONTEND_IMAGE}:${env.BUILD_ID}"
                sh "docker push ${BACKEND_IMAGE}:${env.BUILD_ID}"
                
                // Also push latest tags
                sh "docker tag ${FRONTEND_IMAGE}:${env.BUILD_ID} ${FRONTEND_IMAGE}:latest"
                sh "docker tag ${BACKEND_IMAGE}:${env.BUILD_ID} ${BACKEND_IMAGE}:latest"
                
                sh "docker push ${FRONTEND_IMAGE}:latest"
                sh "docker push ${BACKEND_IMAGE}:latest"
            }
        }

        stage('Helm Lint') {
            steps {
                echo 'Linting Helm Chart...'
                sh 'helm lint ./helm'
            }
        }

        stage('Update Helm Values') {
            steps {
                echo 'Updating Helm Chart values...'
                // Using a more specific sed command to avoid changing the mongodb tag
                withCredentials([usernamePassword(credentialsId: 'github-credentials', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                    sh """
                    sed -i '/frontend:/,/tag:/ s/tag:.*/tag: ${env.BUILD_ID}/' helm/values.yaml
                    sed -i '/backend:/,/tag:/ s/tag:.*/tag: ${env.BUILD_ID}/' helm/values.yaml
                    git config --global user.email "jenkins@example.com"
                    git config --global user.name "Jenkins Pipeline"
                    git commit -am "Update image tag to ${env.BUILD_ID}"
                    git push https://\${GIT_USERNAME}:\${GIT_PASSWORD}@github.com/Arun-KumarRavi/login-page.git HEAD:main
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution finished.'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
