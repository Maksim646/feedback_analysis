.PHONY: help install install-clean install-full test test-imports run build clean docker-build docker-run docker-stop

# Default target
help:
	@echo "NLP Worker Service - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install      - Install basic dependencies (NLTK only)"
	@echo "  install-clean - Install minimal tested dependencies"
	@echo "  install-full - Install all dependencies including spaCy and TextBlob"
	@echo "  run          - Run the service locally"
	@echo "  test         - Run tests"
	@echo "  test-imports - Test all imports work correctly"
	@echo "  clean        - Clean up generated files"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker services"
	@echo ""
	@echo "Utilities:"
	@echo "  proto-gen    - Generate protobuf files"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code"

# Install basic dependencies
install:
	@echo "📚 Installing basic dependencies..."
	pip install -r requirements.txt
	@echo "🤖 Downloading NLTK data..."
	python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"
	@echo "✅ Basic installation complete!"

# Install clean minimal dependencies
install-clean:
	@echo "🧹 Installing clean minimal dependencies..."
	pip install -r requirements-clean.txt
	@echo "🤖 Downloading NLTK data..."
	python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"
	@echo "✅ Clean installation complete!"

# Install full dependencies including optional packages
install-full:
	@echo "📚 Installing full dependencies..."
	pip install -r requirements.txt
	pip install textblob==0.17.1 spacy==3.7.2
	@echo "🤖 Downloading NLTK data..."
	python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"
	@echo "🔍 Downloading spaCy model..."
	python3 -m spacy download en_core_web_sm
	@echo "✅ Full installation complete!"

# Run the service locally
run:
	@echo "🚀 Starting NLP Worker Service..."
	python3 cmd/main.py

# Test imports
test-imports:
	@echo "🧪 Testing imports..."
	python3 test_imports.py

# Run tests
test: test-imports
	@echo ""
	@echo "🧪 Running service tests..."
	python3 test_service.py
	@echo ""
	@echo "🔍 Running integration tests..."
	python3 integration_test.py

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "✅ Cleanup complete!"

# Build Docker image
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t nlp-worker-service .

# Run with Docker Compose
docker-run:
	@echo "🚀 Starting services with Docker Compose..."
	docker-compose up -d
	@echo "✅ Services started! Check with: docker-compose ps"

# Stop Docker services
docker-stop:
	@echo "🛑 Stopping Docker services..."
	docker-compose down
	@echo "✅ Services stopped!"

# Generate protobuf files (if needed)
proto-gen:
	@echo "📝 Generating protobuf files..."
	python3 -m grpc_tools.protoc \
		--python_out=proto/nlp_worker_reader \
		--grpc_python_out=proto/nlp_worker_reader \
		--proto_path=proto/nlp_worker_reader \
		proto/nlp_worker_reader/nlp_worker_reader.proto
	@echo "✅ Protobuf files generated!"

# Run code linting
lint:
	@echo "🔍 Running code linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 . --max-line-length=120 --ignore=E501,W503; \
	else \
		echo "⚠️  flake8 not installed. Install with: pip install flake8"; \
	fi

# Format code
format:
	@echo "🎨 Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black . --line-length=120; \
	else \
		echo "⚠️  black not installed. Install with: pip install black"; \
	fi

# Quick start (install + run)
quick-start: install run

# Quick start with clean dependencies
quick-start-clean: install-clean run

# Development setup
dev-setup: install proto-gen
	@echo "✅ Development environment ready!"
	@echo "Run 'make run' to start the service"
