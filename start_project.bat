@echo off
chcp 65001 >nul
echo 🚀 Starting Feedback Analysis Project...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Start infrastructure services
echo 📡 Starting infrastructure services...
cd infrastructure
docker-compose up -d
cd ..

REM Wait for services to start
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Start NLP Worker service
echo 🔧 Starting NLP Worker service...
cd proto\nlp_worker
docker-compose up -d
cd ..\..

REM Show service status
echo.
echo 📊 Service Status:
echo ==================
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo 🌐 Service URLs:
echo MongoDB: localhost:27017
echo Kafka: localhost:9092
echo Kafka UI: http://localhost:8080
echo Redis: localhost:6379
echo Redis Commander: http://localhost:8081
echo Jaeger: http://localhost:16686
echo Prometheus: http://localhost:9090
echo Grafana: http://localhost:3000 (admin/admin123)

echo.
echo 🎉 All services are running!
echo.
echo Next steps:
echo 1. Test the NLP Worker: python simulate_nlp_worker.py
echo 2. Monitor services in Grafana: http://localhost:3000
echo 3. View traces in Jaeger: http://localhost:16686
echo 4. Check Kafka topics: http://localhost:8080

pause

