// Jenkinsfile

pipeline {
    agent any

    environment {
        REGISTRY_URL = "your-registry.example.com"
        IMAGE_NAME   = "slm-lab"
        IMAGE_TAG    = "latest"
        K8S_CONTEXT  = "your-k8s-context"  // 필요시 변경
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install deps & Test') {
            steps {
                sh '''
                python -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                # 간단한 문법 검사 정도만 (pytest 있으면 pytest로 대체)
                python -m compileall app
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG} .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                sh '''
                docker push ${REGISTRY_URL}/${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                # kubeconfig / context는 Jenkins 노드에 세팅되어 있다고 가정
                kubectl --context=${K8S_CONTEXT} apply -f k8s/deployment.yaml
                kubectl --context=${K8S_CONTEXT} apply -f k8s/service.yaml
                '''
            }
        }
    }
}
