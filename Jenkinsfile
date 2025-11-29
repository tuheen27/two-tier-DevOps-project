pipeline {
    agent any

    environment {
        // Docker Hub Configuration
        DOCKERHUB_CREDENTIALS = 'DOCKER'
        DOCKERHUB_IMAGE = 'tuheen27/two-tier-frontend-application:latest'
        
        // MongoDB Configuration (for testing)
        MONGO_IMAGE = 'mongo:7.0'
        MONGO_CONTAINER = 'mongodb-test'
        
        // Application Test Configuration
        APP_CONTAINER = 'flask-app-test'
        TEST_PORT = '5001'
        MONGO_PORT = '27018'  // Use different port to avoid conflicts
        
        // MongoDB Credentials
        MONGO_USERNAME = 'admin'
        MONGO_PASSWORD = 'password123'
        MONGO_DB = 'flask_app'
    }

    stages {
        stage('Docker Hub Login') {
            steps {
                echo '========== Logging into Docker Hub =========='
                script {
                    withCredentials([usernamePassword(
                        credentialsId: "${DOCKERHUB_CREDENTIALS}",
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        bat 'echo %DOCKER_PASS% | docker login -u "%DOCKER_USER%" --password-stdin'
                        echo '✅ Docker Hub login successful'
                    }
                }
            }
        }

        stage('Cleanup Old Containers') {
            steps {
                echo '========== Cleaning Up Old Test Containers =========='
                bat """
                    docker stop %APP_CONTAINER% 2>nul || echo Skipped
                    docker stop %MONGO_CONTAINER% 2>nul || echo Skipped
                    docker rm %APP_CONTAINER% 2>nul || echo Skipped
                    docker rm %MONGO_CONTAINER% 2>nul || echo Skipped
                    docker rm -f %APP_CONTAINER% 2>nul || echo Skipped
                    docker rm -f %MONGO_CONTAINER% 2>nul || echo Skipped
                    echo ✅ Old containers cleaned up
                """
            }
        }

        stage('Start MongoDB') {
            steps {
                echo '========== Starting MongoDB Container =========='
                bat """
                    docker run -d --name %MONGO_CONTAINER% -p %MONGO_PORT%:27017 -e MONGO_INITDB_ROOT_USERNAME=%MONGO_USERNAME% -e MONGO_INITDB_ROOT_PASSWORD=%MONGO_PASSWORD% %MONGO_IMAGE%
                    echo ⏳ Waiting for MongoDB to be ready...
                    timeout /t 10 /nobreak
                    echo ✅ MongoDB started successfully
                    docker ps | findstr %MONGO_CONTAINER%
                """
            }
        }

        stage('Pull Latest Application Image') {
            steps {
                echo '========== Pulling Latest Image from Docker Hub =========='
                bat """
                    docker pull %DOCKERHUB_IMAGE%
                    echo ✅ Image pulled successfully
                    docker images | findstr two-tier-frontend-application
                """
            }
        }

        stage('Run Application') {
            steps {
                echo '========== Starting Flask Application Container =========='
                bat """
                    docker run -d --name %APP_CONTAINER% -p %TEST_PORT%:5000 --link %MONGO_CONTAINER%:mongodb -e MONGO_HOST=%MONGO_CONTAINER% -e MONGO_PORT=27017 -e MONGO_USERNAME=%MONGO_USERNAME% -e MONGO_PASSWORD=%MONGO_PASSWORD% -e MONGO_AUTH_SOURCE=admin -e MONGO_DB_NAME=%MONGO_DB% -e MONGO_COLLECTION_NAME=users %DOCKERHUB_IMAGE%
                    echo ⏳ Waiting for application to start...
                    timeout /t 15 /nobreak
                    echo ✅ Application started successfully
                    docker ps | findstr %APP_CONTAINER%
                """
            }
        }

        stage('Test Health Endpoint') {
            steps {
                echo '========== Testing Health Endpoint =========='
                powershell """
                    Write-Host '🔍 Testing /health endpoint...'
                    \$response = Invoke-WebRequest -Uri "http://localhost:${env:TEST_PORT}/health" -UseBasicParsing
                    Write-Host "Response: \$($response.Content)"
                    
                    if (\$response.Content -match 'healthy') {
                        Write-Host '✅ Health check PASSED'
                    } else {
                        Write-Host '❌ Health check FAILED'
                        exit 1
                    }
                """
            }
        }

        stage('Test Home Page') {
            steps {
                echo '========== Testing Home Page =========='
                powershell """
                    Write-Host '🔍 Testing home page (/)...'
                    \$response = Invoke-WebRequest -Uri "http://localhost:${env:TEST_PORT}/" -UseBasicParsing
                    Write-Host "HTTP Status: \$($response.StatusCode)"
                    
                    if (\$response.StatusCode -eq 200) {
                        Write-Host '✅ Home page test PASSED'
                    } else {
                        Write-Host '❌ Home page test FAILED'
                        exit 1
                    }
                """
            }
        }

        stage('Test Users Endpoint') {
            steps {
                echo '========== Testing Users Endpoint =========='
                powershell """
                    Write-Host '🔍 Testing /users endpoint...'
                    \$response = Invoke-WebRequest -Uri "http://localhost:${env:TEST_PORT}/users" -UseBasicParsing
                    Write-Host "Response: \$($response.Content)"
                    
                    if (\$response.Content -match 'success') {
                        Write-Host '✅ Users endpoint test PASSED'
                    } else {
                        Write-Host '❌ Users endpoint test FAILED'
                        exit 1
                    }
                """
            }
        }

        stage('Test Data Submission') {
            steps {
                echo '========== Testing Data Submission =========='
                powershell """
                    Write-Host '🔍 Testing POST /submit endpoint...'
                    \$body = @{
                        name = 'Jenkins Test User'
                        email = 'jenkins@test.com'
                        phone = '1234567890'
                    } | ConvertTo-Json
                    
                    \$response = Invoke-WebRequest -Uri "http://localhost:${env:TEST_PORT}/submit" -Method POST -Body \$body -ContentType 'application/json' -UseBasicParsing
                    Write-Host "Response: \$($response.Content)"
                    
                    if (\$response.Content -match 'success') {
                        Write-Host '✅ Data submission test PASSED'
                    } else {
                        Write-Host '❌ Data submission test FAILED'
                        exit 1
                    }
                """
            }
        }

        stage('Verify Data in Database') {
            steps {
                echo '========== Verifying Data Stored in Database =========='
                powershell """
                    Write-Host '🔍 Retrieving users from database...'
                    \$response = Invoke-WebRequest -Uri "http://localhost:${env:TEST_PORT}/users" -UseBasicParsing
                    Write-Host "Response: \$($response.Content)"
                    
                    if (\$response.Content -match 'Jenkins Test User') {
                        Write-Host '✅ Database verification PASSED'
                    } else {
                        Write-Host '❌ Database verification FAILED'
                        exit 1
                    }
                """
            }
        }

        stage('View Application Logs') {
            steps {
                echo '========== Displaying Application Logs =========='
                bat """
                    echo 📋 Flask Application Logs:
                    docker logs --tail 30 %APP_CONTAINER%
                    echo.
                    echo 📋 MongoDB Logs:
                    docker logs --tail 20 %MONGO_CONTAINER%
                """
            }
        }
    }

    post {
        success {
            echo '''
            ╔════════════════════════════════════════════════════════════╗
            ║          ✅ ALL TESTS PASSED SUCCESSFULLY ✅              ║
            ╠════════════════════════════════════════════════════════════╣
            ║  📦 Image: tuheen27/two-tier-frontend-application:latest  ║
            ║  🌐 Application: http://localhost:5001                     ║
            ║  🗄️  MongoDB: localhost:27018                             ║
            ║                                                            ║
            ║  Test Results:                                             ║
            ║    ✅ Health Check - PASSED                               ║
            ║    ✅ Home Page - PASSED                                  ║
            ║    ✅ Users Endpoint - PASSED                             ║
            ║    ✅ Data Submission - PASSED                            ║
            ║    ✅ Database Verification - PASSED                      ║
            ╚════════════════════════════════════════════════════════════╝
            '''
        }
        
        failure {
            echo '''
            ╔════════════════════════════════════════════════════════════╗
            ║                    ❌ TESTS FAILED ❌                      ║
            ╠════════════════════════════════════════════════════════════╣
            ║  Check logs above for detailed error information          ║
            ╚════════════════════════════════════════════════════════════╝
            '''
            
            // Display detailed logs on failure
            bat """
                echo 📋 Full Application Logs:
                docker logs %APP_CONTAINER% 2>&1 || echo No app logs available
                echo.
                echo 📋 Full MongoDB Logs:
                docker logs %MONGO_CONTAINER% 2>&1 || echo No MongoDB logs available
            """
        }
        
        cleanup {
            echo '========== Cleaning Up Test Environment =========='
            bat """
                docker stop %APP_CONTAINER% %MONGO_CONTAINER% 2>nul || echo Skipped
                docker rm %APP_CONTAINER% %MONGO_CONTAINER% 2>nul || echo Skipped
                docker logout || echo Skipped
                echo ✅ Cleanup completed
            """
        }
    }
}
