pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = 'DOCKER'
        DOCKERHUB_IMAGE = 'tuheen27/two-tier-frontend-application:latest'
        AWS_CREDENTIALS = 'AWS_CREDENTIALS'
        AWS_REGION = 'ap-south-1'
        ECR_REPOSITORY = 'dockerimage'
        ECR_URI = '744709874293.dkr.ecr.ap-south-1.amazonaws.com/dockerimage:latest'
    }

    triggers {
        cron('H/5 * * * *')
    }

    stages {
        stage('Pull from Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDENTIALS, usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        bat 'echo %PASS% | docker login -u %USER% --password-stdin'
                    }
                    bat 'docker pull %DOCKERHUB_IMAGE%'
                }
            }
        }

        stage('Test Image') {
            steps {
                bat '''
                    docker network create app-network 2>nul || echo Network exists
                    docker run -d --name mongodb --network app-network -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password123 mongo:7.0
                    timeout /t 10 /nobreak
                    docker run -d --name flask_application --network app-network -p 5000:5000 -e MONGO_HOST=mongodb -e MONGO_PORT=27017 -e MONGO_USERNAME=admin -e MONGO_PASSWORD=password123 -e MONGO_AUTH_SOURCE=admin -e MONGO_DB_NAME=flask_app -e MONGO_COLLECTION_NAME=users %DOCKERHUB_IMAGE%
                    timeout /t 15 /nobreak
                '''
                powershell '''
                    Write-Host "Testing application endpoints..."
                    
                    $health = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing
                    if ($health.Content -notmatch 'healthy') { 
                        Write-Host "❌ Health check failed"
                        exit 1 
                    }
                    Write-Host "✅ Health check passed"
                    
                    $home = Invoke-WebRequest -Uri "http://localhost:5000/" -UseBasicParsing
                    if ($home.StatusCode -ne 200) { 
                        Write-Host "❌ Home page failed"
                        exit 1 
                    }
                    Write-Host "✅ Home page passed"
                    
                    $users = Invoke-WebRequest -Uri "http://localhost:5000/users" -UseBasicParsing
                    if ($users.Content -notmatch 'success') { 
                        Write-Host "❌ Users endpoint failed"
                        exit 1 
                    }
                    Write-Host "✅ Users endpoint passed"
                    
                    Write-Host "✅ All tests passed - MongoDB connection verified"
                '''
                bat '''
                    docker stop flask_application mongodb
                    docker rm flask_application mongodb
                    docker network rm app-network 2>nul || echo Network cleanup
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: AWS_CREDENTIALS]]) {
                        bat '''
                            aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin 744709874293.dkr.ecr.ap-south-1.amazonaws.com
                            docker tag %DOCKERHUB_IMAGE% %ECR_URI%
                            docker push %ECR_URI%
                            echo ✅ Pushed to ECR: %ECR_URI%
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            bat '''
                docker stop flask_application mongodb 2>nul || echo Skipped
                docker rm flask_application mongodb 2>nul || echo Skipped
                docker network rm app-network 2>nul || echo Skipped
                docker logout 2>nul || echo Done
            '''
        }
        success {
            echo '✅ Pipeline Completed - Image pulled, tested with MongoDB on port 5000, and pushed to ECR'
        }
        failure {
            bat 'docker logs flask_application 2>&1 || echo No logs'
            echo '❌ Pipeline Failed'
        }
    }
}
