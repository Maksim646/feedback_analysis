# NLP Worker Service

A microservice for analyzing feedback comments using Natural Language Processing (NLP) to extract sentiment and keywords.

## Features

- **Sentiment Analysis**: Determines if feedback is positive, negative, or neutral
- **Keyword Extraction**: Identifies important words and phrases from feedback text
- **gRPC API**: High-performance communication protocol
- **MongoDB Storage**: Persistent storage of analysis results
- **Prometheus Metrics**: Monitoring and observability
- **Health Checks**: Kubernetes-ready health endpoints
- **Docker Support**: Containerized deployment
- **Flexible Dependencies**: Works with minimal setup or enhanced with optional packages

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway  │───▶│  NLP Worker      │───▶│    MongoDB      │
│   (Golang)     │    │  (Python)        │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Prometheus      │
                       │  Metrics         │
                       └──────────────────┘
```

## Prerequisites

- Python 3.11+
- MongoDB
- Docker (optional)

## Installation

### Quick Start (Recommended)

For the most reliable installation with tested dependencies:

```bash
cd proto/nlp_worker
make install-clean
```

### Alternative Installation Options

#### Basic Installation (NLTK only)
```bash
cd proto/nlp_worker
make install
```

#### Full Installation (Enhanced with spaCy and TextBlob)
```bash
cd proto/nlp_worker
make install-full
```

### Manual Installation

1. **Clone the repository**
   ```bash
   cd proto/nlp_worker
   ```

2. **Install clean dependencies (recommended)**
   ```bash
   pip install -r requirements-clean.txt
   ```

3. **Or install minimal dependencies**
   ```bash
   pip install -r requirements-minimal.txt
   ```

4. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"
   ```

5. **Optional: Install enhanced packages**
   ```bash
   pip install textblob==0.17.1 spacy==3.7.2
   python -m spacy download en_core_web_sm
   ```

6. **Configure the service**
   - Edit `config/config.yaml` with your MongoDB and other service configurations

### Docker

1. **Build the image**
   ```bash
   docker build -t nlp-worker-service .
   ```

2. **Run the container**
   ```bash
   docker run -p 5003:5003 -p 3003:3003 -p 8003:8003 nlp-worker-service
   ```

## Configuration

The service configuration is in `config/config.yaml`:

```yaml
serviceName: nlp_worker_service
grpc:
  port: 5003
  development: true

nlp:
  model_name: "en_core_web_sm"
  sentiment_threshold: 0.1
  max_keywords: 10
  language: "en"

mongo:
  uri: "mongodb://localhost:27017"
  db: feedback_analysis
  collections:
    feedback_analysis: feedback_analysis
```

## Usage

### Starting the Service

```bash
# Using Makefile (recommended)
make run

# Quick start with clean dependencies
make quick-start-clean

# Or directly
python cmd/main.py

# Or using startup script
./start.sh
```

The service will start:
- gRPC server on port 5003
- Health check server on port 3003
- Prometheus metrics on port 8003

### API Endpoints

#### Health Checks
- `GET /ready` - Readiness probe
- `GET /live` - Liveness probe
- `GET /metrics` - Service metrics

#### gRPC Service

**CreateFeedbackAnalysis**
```protobuf
service NlpWorkerService {
  rpc CreateFeedbackAnalysis(CreateFeedbackAnalysisReq) returns (CreateFeedbackAnalysisRes);
}

message CreateFeedbackAnalysisReq {
  string feedback_id = 1;
  string feedback_source = 2;
  string text = 3;
  google.protobuf.Timestamp created_at = 4;
}

message CreateFeedbackAnalysisRes {
  string feedback_id = 1;
  string feedback_source = 2;
  string text = 3;
  google.protobuf.Timestamp created_at = 4;
  string keywords = 5;
  string sentiment = 6;
}
```

### Example Client Usage

```python
import grpc
from proto.nlp_worker_reader import nlp_worker_reader_pb2, nlp_worker_reader_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

# Create channel
channel = grpc.insecure_channel('localhost:5003')
stub = nlp_worker_reader_pb2_grpc.NlpWorkerServiceStub(channel)

# Create request
timestamp = Timestamp()
timestamp.FromDatetime(datetime.utcnow())

request = nlp_worker_reader_pb2.CreateFeedbackAnalysisReq(
    feedback_id="feedback_123",
    feedback_source="customer_support",
    text="I love this product! It's amazing and works perfectly.",
    created_at=timestamp
)

# Make request
response = stub.CreateFeedbackAnalysis(request)
print(f"Sentiment: {response.sentiment}")
print(f"Keywords: {response.keywords}")
```

## Testing

Run the test script to verify the service:

```bash
# Basic test
python test_service.py

# Full integration test
python integration_test.py

# Or using Makefile
make test
```

This will test the service with sample feedback texts and verify sentiment analysis accuracy.

## Monitoring

### Prometheus Metrics

The service exposes Prometheus metrics on port 8003:

- `nlp_worker_grpc_requests_total` - Total gRPC requests
- `nlp_worker_feedback_analysis_duration_seconds` - Analysis processing time
- `nlp_worker_sentiment_distribution_total` - Sentiment distribution
- `nlp_worker_keyword_count` - Keywords extracted per feedback

### Health Checks

- **Readiness**: `http://localhost:3003/ready`
- **Liveness**: `http://localhost:3003/live`

## Integration with API Gateway

The NLP Worker service is designed to work with the Golang API Gateway. The gateway can:

1. Receive feedback from various sources
2. Send feedback to the NLP Worker for analysis
3. Store results in the database
4. Provide analysis results via REST API

## Deployment

### Kubernetes

The service includes Kubernetes manifests in the parent directory:

```bash
kubectl apply -f ../../k8s/deployments/
```

### Docker Compose

```yaml
version: '3.8'
services:
  nlp-worker:
    build: .
    ports:
      - "5003:5003"
      - "3003:3003"
      - "8003:8003"
    environment:
      - MONGODB_URI=mongodb://mongo:27017
    depends_on:
      - mongo
```

## Troubleshooting

### Common Issues

1. **Dependency conflicts**
   - Use `make install-clean` for the most reliable installation
   - Check Python version compatibility (3.11+ recommended)

2. **NLP models not found**
   - Basic installation: Ensure NLTK data is downloaded
   - Enhanced installation: Check spaCy model is available

3. **MongoDB connection failed**
   - Verify MongoDB is running and accessible
   - Check connection string in config

4. **Port conflicts**
   - Ensure ports 5003, 3003, and 8003 are available
   - Modify config.yaml if needed

### Logs

The service logs to stdout with structured JSON format. Check logs for:

- Service startup messages
- NLP model initialization
- gRPC request processing
- Error details

## Development

### Project Structure

```
nlp_worker/
├── cmd/
│   └── main.py                 # Service entry point
├── config/
│   ├── config.py               # Configuration classes
│   └── config.yaml             # Configuration file
├── internal/
│   ├── feedback_analysis/      # Core business logic
│   │   ├── delivery/           # API layer
│   │   ├── models/             # Data models
│   │   ├── repository/         # Data access
│   │   └── service/            # Business logic
│   ├── metrics/                # Prometheus metrics
│   └── server/                 # Server implementation
├── proto/                      # Protobuf definitions
├── Dockerfile                  # Container definition
├── requirements-clean.txt      # Clean tested dependencies (recommended)
├── requirements-minimal.txt    # Minimal dependencies
├── requirements.txt            # Full dependencies
└── README.md                   # This file
```

### Adding New Features

1. **New NLP capabilities**: Extend `FeedbackAnalysisService`
2. **Additional endpoints**: Add new gRPC methods in proto files
3. **Storage changes**: Modify repository classes
4. **Metrics**: Add new Prometheus metrics

## License

This project is part of the feedback analysis system.
