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
                        sh 'echo $DOCKER_PASS | docker login -u "$DOCKER_USER" --password-stdin'
                        echo '✅ Docker Hub login successful'
                    }
                }
            }
        }

        stage('Cleanup Old Containers') {
            steps {
                echo '========== Cleaning Up Old Test Containers =========='
                sh """
                    docker stop ${APP_CONTAINER} ${MONGO_CONTAINER} 2>/dev/null || true
                    docker rm ${APP_CONTAINER} ${MONGO_CONTAINER} 2>/dev/null || true
                    echo '✅ Old containers cleaned up'
                """
            }
        }

        stage('Start MongoDB') {
            steps {
                echo '========== Starting MongoDB Container =========='
                sh """
                    docker run -d \
                      --name ${MONGO_CONTAINER} \
                      -p ${MONGO_PORT}:27017 \
                      -e MONGO_INITDB_ROOT_USERNAME=${MONGO_USERNAME} \
                      -e MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD} \
                      ${MONGO_IMAGE}
                    
                    echo '⏳ Waiting for MongoDB to be ready...'
                    sleep 10
                    
                    echo '✅ MongoDB started successfully'
                    docker ps | grep ${MONGO_CONTAINER}
                """
            }
        }

        stage('Pull Latest Application Image') {
            steps {
                echo '========== Pulling Latest Image from Docker Hub =========='
                sh """
                    docker pull ${DOCKERHUB_IMAGE}
                    echo '✅ Image pulled successfully'
                    docker images | grep two-tier-frontend-application
                """
            }
        }

        stage('Run Application') {
            steps {
                echo '========== Starting Flask Application Container =========='
                sh """
                    docker run -d \
                      --name ${APP_CONTAINER} \
                      -p ${TEST_PORT}:5000 \
                      --link ${MONGO_CONTAINER}:mongodb \
                      -e MONGO_HOST=${MONGO_CONTAINER} \
                      -e MONGO_PORT=27017 \
                      -e MONGO_USERNAME=${MONGO_USERNAME} \
                      -e MONGO_PASSWORD=${MONGO_PASSWORD} \
                      -e MONGO_AUTH_SOURCE=admin \
                      -e MONGO_DB_NAME=${MONGO_DB} \
                      -e MONGO_COLLECTION_NAME=users \
                      ${DOCKERHUB_IMAGE}
                    
                    echo '⏳ Waiting for application to start...'
                    sleep 15
                    
                    echo '✅ Application started successfully'
                    docker ps | grep ${APP_CONTAINER}
                """
            }
        }

        stage('Test Health Endpoint') {
            steps {
                echo '========== Testing Health Endpoint =========='
                sh """
                    echo '🔍 Testing /health endpoint...'
                    RESPONSE=\$(curl -s http://localhost:${TEST_PORT}/health)
                    echo "Response: \$RESPONSE"
                    
                    # Check if response contains "healthy"
                    if echo "\$RESPONSE" | grep -q "healthy"; then
                        echo '✅ Health check PASSED'
                    else
                        echo '❌ Health check FAILED'
                        exit 1
                    fi
                """
            }
        }

        stage('Test Home Page') {
            steps {
                echo '========== Testing Home Page =========='
                sh """
                    echo '🔍 Testing home page (/)...'
                    STATUS=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${TEST_PORT}/)
                    echo "HTTP Status: \$STATUS"
                    
                    if [ "\$STATUS" = "200" ]; then
                        echo '✅ Home page test PASSED'
                    else
                        echo '❌ Home page test FAILED'
                        exit 1
                    fi
                """
            }
        }

        stage('Test Users Endpoint') {
            steps {
                echo '========== Testing Users Endpoint =========='
                sh """
                    echo '🔍 Testing /users endpoint...'
                    RESPONSE=\$(curl -s http://localhost:${TEST_PORT}/users)
                    echo "Response: \$RESPONSE"
                    
                    # Check if response contains "success"
                    if echo "\$RESPONSE" | grep -q "success"; then
                        echo '✅ Users endpoint test PASSED'
                    else
                        echo '❌ Users endpoint test FAILED'
                        exit 1
                    fi
                """
            }
        }

        stage('Test Data Submission') {
            steps {
                echo '========== Testing Data Submission =========='
                sh """
                    echo '🔍 Testing POST /submit endpoint...'
                    RESPONSE=\$(curl -s -X POST http://localhost:${TEST_PORT}/submit \
                      -H "Content-Type: application/json" \
                      -d '{"name":"Jenkins Test User","email":"jenkins@test.com","phone":"1234567890"}')
                    
                    echo "Response: \$RESPONSE"
                    
                    # Check if submission was successful
                    if echo "\$RESPONSE" | grep -q "success"; then
                        echo '✅ Data submission test PASSED'
                    else
                        echo '❌ Data submission test FAILED'
                        exit 1
                    fi
                """
            }
        }

        stage('Verify Data in Database') {
            steps {
                echo '========== Verifying Data Stored in Database =========='
                sh """
                    echo '🔍 Retrieving users from database...'
                    RESPONSE=\$(curl -s http://localhost:${TEST_PORT}/users)
                    echo "Response: \$RESPONSE"
                    
                    # Check if our test user exists
                    if echo "\$RESPONSE" | grep -q "Jenkins Test User"; then
                        echo '✅ Database verification PASSED'
                    else
                        echo '❌ Database verification FAILED'
                        exit 1
                    fi
                """
            }
        }

        stage('View Application Logs') {
            steps {
                echo '========== Displaying Application Logs =========='
                sh """
                    echo '📋 Flask Application Logs:'
                    docker logs --tail 30 ${APP_CONTAINER}
                    echo ''
                    echo '📋 MongoDB Logs:'
                    docker logs --tail 20 ${MONGO_CONTAINER}
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
            sh """
                echo '📋 Full Application Logs:'
                docker logs ${APP_CONTAINER} 2>&1 || echo 'No app logs available'
                echo ''
                echo '📋 Full MongoDB Logs:'
                docker logs ${MONGO_CONTAINER} 2>&1 || echo 'No MongoDB logs available'
            """
        }
        
        cleanup {
            echo '========== Cleaning Up Test Environment =========='
            sh """
                docker stop ${APP_CONTAINER} ${MONGO_CONTAINER} 2>/dev/null || true
                docker rm ${APP_CONTAINER} ${MONGO_CONTAINER} 2>/dev/null || true
                docker logout || true
                echo '✅ Cleanup completed'
            """
        }
    }
}
