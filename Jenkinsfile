pipeline {
    agent any

    parameters {
        string(
            name: 'SUBDOMAINS',
            defaultValue: 'example1.com,example2.com,example3.com',
            description: 'Comma-separated list of subdomains to monitor.'
        )

        string(
            name: 'RETRIES',
            defaultValue: '3',
            description: 'Amount of retries performed before sending an alert.'
        )

        string(
            name: 'SLEEP_TIME',
            defaultValue: '60',
            description: 'Amount of time on sleep before pinging the website again.'
        )

        string(
            name: 'DELAY_BEFORE_RETRYING',
            defaultValue: '60',
            description: 'Delay between retries.'
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
                                -e SLEEP_TIME='${params.SLEEP_TIME}' \
                                -e RETRIES='${params.RETRIES}' \
                                -e DELAY_BEFORE_RETRYING='${params.DELAY_BEFORE_RETRYING}' \
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

