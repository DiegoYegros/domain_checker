pipeline {
    agent any

    parameters {
        string(
            name: 'SUBDOMAINS',
            defaultValue: 'example1.com,example2.com,example3.com',
            description: 'Comma-separated list of subdomains to monitor.'
        )
    }

    environment {
        DOCKER_IMAGE = "domain_checker:${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/diegoyegros/domain_checker.git',
                    credentialsId: 'github-credentials'
            }
        }

        stage('Validate Subdomains') {
            steps {
                script {
                    def subdomains = params.SUBDOMAINS.split(',')
                    subdomains.each { subdomain ->
                        if (!subdomain.trim().matches(/^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$/)) {
                            error "Invalid subdomain format: ${subdomain}"
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build(DOCKER_IMAGE)
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    docker.image(DOCKER_IMAGE).inside {
                        sh 'python -m unittest discover tests'
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'bot-token', variable: 'BOT_TOKEN'),
                        string(credentialsId: 'chat-id', variable: 'CHAT_ID')
                    ]) {
                        sh '''
                            docker stop domain_checker || true
                            docker rm domain_checker || true
                        '''

                        sh """
                            docker run -d \
                                --name domain_checker \
                                -e BOT_TOKEN=${BOT_TOKEN} \
                                -e CHAT_ID=${CHAT_ID} \
                                -e SUBDOMAINS='${params.SUBDOMAINS}' \
                                -p 8000:8000 \
                                ${DOCKER_IMAGE}
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs for details.'
        }
    }
}

