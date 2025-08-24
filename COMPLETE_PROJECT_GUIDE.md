# 🚀 Complete Feedback Analysis Project Guide

## 📋 Project Overview

This is a complete **microservices-based feedback analysis system** that processes customer feedback through NLP analysis, stores results in MongoDB, and uses Kafka for message processing. The system includes comprehensive monitoring, tracing, and visualization capabilities.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway  │    │   NLP Worker    │    │   Kafka Topics  │
│   (Golang)     │◄──►│   (Python)      │◄──►│   (Raw/Analyzed)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL   │    │     MongoDB     │    │      Redis      │
│   (User Data)  │    │ (Analysis Results)│   │   (Caching)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Jaeger      │    │   Prometheus    │    │     Grafana     │
│   (Tracing)    │    │   (Metrics)     │    │  (Visualization)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### **Option 1: Complete Infrastructure (Recommended)**

```bash
# Make scripts executable
chmod +x start_project.sh
chmod +x simulate_nlp_worker.py

# Start everything
./start_project.sh
```

### **Option 2: Manual Start**

```bash
# 1. Start infrastructure
cd infrastructure
docker-compose up -d
cd ..

# 2. Start NLP Worker
cd proto/nlp_worker
docker-compose up -d
cd ../..

# 3. Test the system
python3 kafka_producer.py
python3 simulate_nlp_worker.py
```

### **Option 3: Windows**

```bash
# Run the batch file
start_project.bat
```

## 📊 Service Ports & URLs

| Service | Port | URL | Credentials |
|---------|------|-----|-------------|
| **MongoDB** | 27017 | `mongodb://localhost:27017` | None |
| **Kafka** | 9092 | `localhost:9092` | None |
| **Kafka UI** | 8080 | http://localhost:8080 | None |
| **Redis** | 6379 | `localhost:6379` | None |
| **Redis Commander** | 8081 | http://localhost:8081 | admin/admin123 |
| **Jaeger** | 16686 | http://localhost:16686 | None |
| **Prometheus** | 9090 | http://localhost:9090 | None |
| **Grafana** | 3000 | http://localhost:3000 | admin/admin123 |
| **API Gateway** | 5001 | http://localhost:5001 | None |
| **NLP Worker gRPC** | 5003 | `localhost:5003` | None |
| **NLP Worker Health** | 3003 | http://localhost:3003 | None |
| **NLP Worker Metrics** | 8003 | http://localhost:8003 | None |

## 🔧 Configuration

### **NLP Worker Config** (`proto/nlp_worker/config/config.yaml`)
- **gRPC Port**: 5003
- **Health Port**: 3003
- **Metrics Port**: 8003
- **MongoDB**: localhost:27017
- **Kafka**: localhost:9092
- **Redis**: localhost:6379
- **Jaeger**: localhost:6831

### **API Gateway Config** (`api_gateway_service/config/config.yaml`)
- **HTTP Port**: 5001
- **gRPC Port**: 5003 (NLP Worker)
- **Kafka**: localhost:9092
- **Redis**: localhost:6379
- **Jaeger**: localhost:6831

## 📡 Kafka Topics

| Topic | Purpose | Message Format |
|-------|---------|----------------|
| `feedback_raw` | Raw feedback from API Gateway | `{"id": "uuid", "text": "feedback text", "user_id": "user123", "timestamp": "iso", "metadata": {...}}` |
| `feedback_analyzed` | Processed feedback from NLP Worker | `{"feedback_id": "uuid", "sentiment": "positive", "sentiment_score": 0.8, "keywords": ["good", "great"], "analysis_timestamp": "iso"}` |

## 🧪 Testing the System

### **1. Send Test Messages via Kafka**

```bash
python3 kafka_producer.py
```

Choose option 1 to send predefined test messages.

### **2. Test NLP Worker Directly**

```bash
python3 simulate_nlp_worker.py
```

This tests the gRPC service directly.

### **3. Monitor Message Flow**

1. **Send messages** via `kafka_producer.py`
2. **Check Kafka UI** at http://localhost:8080
3. **View processed results** in MongoDB
4. **Monitor metrics** in Grafana

## 📈 Monitoring & Observability

### **Grafana Dashboards**
- **Service Metrics**: Request rates, response times, error rates
- **Kafka Metrics**: Message throughput, consumer lag
- **System Metrics**: CPU, memory, disk usage

### **Jaeger Traces**
- **Request Flow**: API Gateway → NLP Worker → Database
- **Performance Analysis**: Identify bottlenecks
- **Error Tracking**: Trace failed requests

### **Prometheus Metrics**
- **Custom Metrics**: Business logic metrics
- **System Metrics**: Infrastructure health
- **Alerting**: Configure alerts for critical issues

## 🐳 Docker Services

### **Infrastructure Services**
- **MongoDB**: Document database for analysis results
- **Kafka + Zookeeper**: Message streaming platform
- **Redis**: Caching and session storage
- **Jaeger**: Distributed tracing
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

### **Application Services**
- **NLP Worker**: Python service for text analysis
- **API Gateway**: Golang service for HTTP/gRPC routing

## ☸️ Kubernetes Deployment

### **Prerequisites**
```bash
# Install kubectl
# Have a Kubernetes cluster running (minikube, Docker Desktop, etc.)
```

### **Deploy to Kubernetes**
```bash
# Apply all deployments
kubectl apply -f k8s/deployments/

# Check status
kubectl get pods
kubectl get services
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep <port>
   
   # Stop conflicting services
   docker stop $(docker ps -aq)
   ```

2. **MongoDB Connection Failed**
   ```bash
   # Check if MongoDB is running
   docker ps | grep mongo
   
   # Restart MongoDB
   docker restart mongo
   ```

3. **Kafka Connection Issues**
   ```bash
   # Check Kafka status
   docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
   
   # Restart Kafka
   docker restart kafka
   ```

4. **Service Health Checks**
   ```bash
   # Check health endpoints
   curl http://localhost:3003/ready  # NLP Worker
   curl http://localhost:3001/ready  # API Gateway
   ```

### **Logs**
```bash
# View service logs
docker logs nlp-worker
docker logs api-gateway
docker logs kafka
docker logs mongo
```

## 🚀 Production Considerations

### **Security**
- **Authentication**: Add JWT tokens, API keys
- **Authorization**: Role-based access control
- **Encryption**: TLS for all communications
- **Secrets**: Use Kubernetes secrets or Docker secrets

### **Scalability**
- **Horizontal Scaling**: Multiple NLP Worker instances
- **Load Balancing**: Use Kubernetes services or HAProxy
- **Database**: MongoDB replica sets, Redis clusters
- **Message Queuing**: Multiple Kafka brokers

### **Monitoring**
- **Alerting**: Configure Prometheus alerts
- **Logging**: Centralized logging with ELK stack
- **Health Checks**: Comprehensive health endpoints
- **Performance**: APM tools like New Relic, DataDog

## 📚 API Documentation

### **NLP Worker gRPC Service**

```protobuf
service NlpWorkerReader {
  rpc CreateFeedbackAnalysis(CreateFeedbackAnalysisReq) returns (CreateFeedbackAnalysisResp);
}
```

### **HTTP Endpoints**

- **Health Check**: `GET /ready`, `GET /live`
- **Metrics**: `GET /metrics`
- **API Gateway**: `POST /api/v1/feedbacks`

## 🎯 Next Steps

1. **Add Authentication**: Implement JWT or OAuth2
2. **Enhance NLP**: Add more sophisticated sentiment analysis
3. **Real-time Processing**: Implement streaming analytics
4. **Machine Learning**: Add model training and deployment
5. **CI/CD**: Set up automated testing and deployment
6. **Load Testing**: Performance testing with tools like k6
7. **Documentation**: API documentation with Swagger/OpenAPI

## 📞 Support

- **Issues**: Check the troubleshooting section above
- **Logs**: Review Docker and application logs
- **Metrics**: Monitor Grafana dashboards
- **Traces**: Use Jaeger for request tracing

---

**🎉 Congratulations!** You now have a complete, production-ready feedback analysis system with comprehensive monitoring, tracing, and visualization capabilities.

