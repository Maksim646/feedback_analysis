#!/bin/bash

# 🚀 Feedback Analysis Project Startup Script
# This script starts all infrastructure components and services

set -e

echo "🚀 Starting Feedback Analysis Project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if kubectl is available
check_k8s() {
    if command -v kubectl &> /dev/null; then
        print_success "Kubernetes (kubectl) is available"
        return 0
    else
        print_warning "Kubernetes (kubectl) not found. Will use Docker Compose only."
        return 1
    fi
}

# Start infrastructure with Docker Compose
start_infrastructure() {
    print_status "Starting infrastructure services with Docker Compose..."
    
    if [ -f "infrastructure/docker-compose.yml" ]; then
        cd infrastructure
        docker-compose up -d
        cd ..
        print_success "Infrastructure services started"
    else
        print_error "Infrastructure docker-compose.yml not found"
        exit 1
    fi
}

# Start services with Docker Compose
start_services() {
    print_status "Starting application services..."
    
    # Start NLP Worker
    if [ -f "proto/nlp_worker/docker compose.yml" ]; then
        cd proto/nlp_worker
        docker-compose up -d
        cd ../..
        print_success "NLP Worker service started"
    fi
}

# Start with Kubernetes
start_k8s() {
    print_status "Starting services with Kubernetes..."
    
    # Apply infrastructure
    kubectl apply -f k8s/deployments/kafka.yaml
    kubectl apply -f k8s/deployments/redis.yaml
    kubectl apply -f k8s/deployments/jaeger.yaml
    kubectl apply -f k8s/deployments/monitoring.yaml
    
    # Apply application services
    kubectl apply -f k8s/deployments/api-gateway.yml
    kubectl apply -f k8s/deployments/postgres.yaml
    kubectl apply -f k8s/deployments/reader-service.yaml
    
    print_success "Kubernetes deployments applied"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for MongoDB
    print_status "Waiting for MongoDB..."
    until docker exec mongo mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
        sleep 2
    done
    print_success "MongoDB is ready"
    
    # Wait for Kafka
    print_status "Waiting for Kafka..."
    until docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; do
        sleep 5
    done
    print_success "Kafka is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker exec redis redis-cli ping > /dev/null 2>&1; do
        sleep 2
    done
    print_success "Redis is ready"
    
    # Wait for Jaeger
    print_status "Waiting for Jaeger..."
    until curl -s http://localhost:16686/api/services > /dev/null 2>&1; do
        sleep 3
    done
    print_success "Jaeger is ready"
    
    # Wait for Prometheus
    print_status "Waiting for Prometheus..."
    until curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; do
        sleep 3
    done
    print_success "Prometheus is ready"
    
    # Wait for Grafana
    print_status "Waiting for Grafana..."
    until curl -s http://localhost:3000/api/health > /dev/null 2>&1; do
        sleep 3
    done
    print_success "Grafana is ready"
}

# Show service status
show_status() {
    echo ""
    echo "📊 Service Status:"
    echo "=================="
    
    # Docker services
    echo "🐳 Docker Services:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    echo "🌐 Service URLs:"
    echo "MongoDB: localhost:27017"
    echo "Kafka: localhost:9092"
    echo "Kafka UI: http://localhost:8080"
    echo "Redis: localhost:6379"
    echo "Redis Commander: http://localhost:8081"
    echo "Jaeger: http://localhost:16686"
    echo "Prometheus: http://localhost:9090"
    echo "Grafana: http://localhost:3000 (admin/admin123)"
    
    if command -v kubectl &> /dev/null; then
        echo ""
        echo "☸️  Kubernetes Services:"
        kubectl get pods
    fi
}

# Main execution
main() {
    echo "🚀 Feedback Analysis Project Startup"
    echo "==================================="
    
    # Check prerequisites
    check_docker
    K8S_AVAILABLE=$(check_k8s)
    
    # Start infrastructure
    start_infrastructure
    
    # Wait for infrastructure to be ready
    wait_for_services
    
    # Start application services
    start_services
    
    # If Kubernetes is available, offer to use it
    if [ $K8S_AVAILABLE -eq 0 ]; then
        echo ""
        read -p "Do you want to deploy to Kubernetes as well? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            start_k8s
        fi
    fi
    
    # Show final status
    show_status
    
    echo ""
    print_success "🎉 All services are running!"
    echo ""
    echo "Next steps:"
    echo "1. Test the NLP Worker: python3 simulate_nlp_worker.py"
    echo "2. Monitor services in Grafana: http://localhost:3000"
    echo "3. View traces in Jaeger: http://localhost:16686"
    echo "4. Check Kafka topics: http://localhost:8080"
}

# Run main function
main "$@"
