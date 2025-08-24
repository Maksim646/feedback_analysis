# 🚀 NLP Worker Service Simulator

A comprehensive simulation tool for testing the NLP Worker microservice. This simulator allows you to send feedback messages to the service and see real-time sentiment analysis and keyword extraction results.

## ✨ Features

- **🧪 Predefined Test Messages**: 6 carefully crafted test cases covering positive, negative, and neutral sentiments
- **💬 Interactive Mode**: Enter your own custom feedback messages
- **📊 Performance Metrics**: Response time measurements and accuracy analysis
- **🎯 Sentiment Validation**: Compare expected vs. actual sentiment results
- **🔌 Easy Integration**: Simple command-line interface with multiple modes
- **📱 Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

1. **NLP Worker Service Running**: Make sure the service is started
   ```bash
   cd proto/nlp_worker
   make run
   ```

2. **Python 3.11+**: Ensure Python is installed and accessible

### Running the Simulator

#### Option 1: Direct Python Execution
```bash
# Run predefined test messages (default)
python3 simulate_nlp_worker.py

# Run in interactive mode
python3 simulate_nlp_worker.py --interactive

# Show help
python3 simulate_nlp_worker.py --help
```

#### Option 2: Using Scripts (Recommended)

**Windows:**
```cmd
simulate_nlp_worker.bat
```

**Unix/Linux/macOS:**
```bash
./simulate_nlp_worker.sh
```

## 📋 Usage Modes

### 1. 🧪 Test Messages Mode (Default)
Runs 6 predefined test messages to verify service functionality:

- **Positive Feedback**: "I absolutely love this product! It exceeded all my expectations..."
- **Negative Feedback**: "This app is completely useless. It crashes every time..."
- **Neutral Feedback**: "The product arrived on time and was packaged well..."
- **Social Media**: "Just tried the new feature and it's amazing! So much faster..."
- **Email Feedback**: "I'm very disappointed with the service. The response time is slow..."
- **Survey Response**: "The product meets basic requirements. It's functional but..."

**Expected Output:**
```
🧪 Running predefined test messages...
==========================================

📝 Test 1/6
   ID: test_001
   Source: customer_support
   Text: I absolutely love this product! It exceeded all my expectations...
   Expected: positive
   ✅ Sentiment: positive
   🔑 Keywords: love, product, exceeded, expectations, quality, outstanding
   ⏱️  Response time: 0.234s
   🎯 Sentiment analysis: CORRECT!
```

### 2. 💬 Interactive Mode
Enter your own feedback messages and see real-time analysis:

```bash
python3 simulate_nlp_worker.py --interactive
```

**Interactive Commands:**
- `quit` - Exit interactive mode
- `help` - Show available commands
- `test` - Run predefined test messages
- `clear` - Clear screen

**Example Session:**
```
💬 Interactive Mode - Enter your own feedback messages
Type 'quit' to exit, 'help' for commands
==========================================

📝 Enter feedback text (or 'quit'/'help'): The customer service was excellent!

🏷️  Source (optional, press Enter for 'custom'): support_ticket

🔄 Analyzing feedback...
   ID: interactive_1703123456
   Source: support_ticket
   Text: The customer service was excellent!

✅ Analysis Complete!
   Sentiment: positive
   Keywords: customer, service, excellent
   Response time: 0.156s
```

### 3. 📚 Help Mode
Display comprehensive usage information:

```bash
python3 simulate_nlp_worker.py --help
```

## 🔧 Configuration Options

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--interactive` | `-i` | Run in interactive mode | `False` |
| `--test-messages` | `-t` | Run predefined test messages | `True` |
| `--host` | | NLP Worker service host | `localhost` |
| `--port` | | NLP Worker service port | `5003` |

### Examples

```bash
# Connect to remote service
python3 simulate_nlp_worker.py --host 192.168.1.100 --port 5003

# Run specific mode
python3 simulate_nlp_worker.py --test-messages
python3 simulate_nlp_worker.py --interactive

# Combine options
python3 simulate_nlp_worker.py --host localhost --port 5003 --interactive
```

## 📊 Understanding Results

### Sentiment Analysis
The service categorizes feedback into three sentiment levels:

- **Positive** (`positive`): Generally favorable feedback
- **Negative** (`negative`): Generally unfavorable feedback  
- **Neutral** (`neutral`): Neither clearly positive nor negative

### Keyword Extraction
Keywords are extracted using NLP techniques:
- Nouns, adjectives, and verbs
- Filtered for relevance and frequency
- Lemmatized for consistency

### Performance Metrics
- **Response Time**: Time from request to response
- **Accuracy**: Percentage of correct sentiment predictions
- **Success Rate**: Percentage of successful API calls

## 🧪 Testing Scenarios

### 1. **Basic Functionality Test**
```bash
# Start the service
cd proto/nlp_worker
make run

# In another terminal, run simulator
python3 simulate_nlp_worker.py
```

### 2. **Load Testing**
```bash
# Run multiple test cycles
for i in {1..5}; do
    echo "=== Test Cycle $i ==="
    python3 simulate_nlp_worker.py --test-messages
    sleep 2
done
```

### 3. **Custom Message Testing**
```bash
# Test specific feedback types
python3 simulate_nlp_worker.py --interactive
```

## 🚨 Troubleshooting

### Common Issues

#### 1. **Connection Failed**
```
❌ Connection failed: [Errno 111] Connection refused
```
**Solution**: Ensure NLP Worker service is running
```bash
cd proto/nlp_worker
make run
```

#### 2. **Import Errors**
```
❌ Import error: No module named 'grpc'
```
**Solution**: Install dependencies
```bash
cd proto/nlp_worker
make install-clean
```

#### 3. **Service Not Responding**
```
❌ gRPC Error: UNAVAILABLE: failed to connect to all addresses
```
**Solution**: Check service status and ports
```bash
# Check if service is listening
netstat -tlnp | grep 5003

# Check service logs
cd proto/nlp_worker
make run
```

### Debug Mode

For detailed debugging, you can modify the simulator to show more information:

```python
# In simulate_nlp_worker.py, add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔌 Integration Examples

### 1. **Automated Testing**
```bash
#!/bin/bash
# test_nlp_service.sh

echo "🧪 Testing NLP Worker Service..."

# Start service
cd proto/nlp_worker
make run &
SERVICE_PID=$!

# Wait for service to start
sleep 5

# Run tests
python3 ../../simulate_nlp_worker.py --test-messages

# Stop service
kill $SERVICE_PID
echo "✅ Testing completed"
```

### 2. **CI/CD Pipeline**
```yaml
# .github/workflows/test-nlp.yml
name: Test NLP Worker Service

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd proto/nlp_worker
          make install-clean
      - name: Start service
        run: |
          cd proto/nlp_worker
          make run &
          sleep 10
      - name: Run simulator tests
        run: |
          python3 simulate_nlp_worker.py --test-messages
```

## 📁 File Structure

```
feedback_analysis/
├── simulate_nlp_worker.py          # Main simulator script
├── simulate_nlp_worker.bat         # Windows batch file
├── simulate_nlp_worker.sh          # Unix shell script
├── SIMULATOR_README.md             # This documentation
└── proto/nlp_worker/               # NLP Worker service
    ├── cmd/main.py                 # Service entry point
    ├── internal/                   # Service implementation
    └── ...
```

## 🎯 Best Practices

### 1. **Testing Strategy**
- Run predefined tests first to verify basic functionality
- Use interactive mode for edge cases and custom scenarios
- Test with various feedback lengths and complexity levels

### 2. **Performance Monitoring**
- Monitor response times during testing
- Track sentiment accuracy over time
- Log any failed requests for analysis

### 3. **Service Management**
- Always start the NLP Worker service before running simulator
- Use `make run` in the nlp_worker directory
- Check service logs for any errors

## 🚀 Next Steps

1. **Run Basic Tests**: Start with predefined test messages
2. **Explore Interactive Mode**: Test your own feedback scenarios
3. **Monitor Performance**: Track response times and accuracy
4. **Integrate with CI/CD**: Add automated testing to your pipeline
5. **Customize Tests**: Modify test messages for your specific use cases

## 🤝 Support

If you encounter issues:

1. **Check Service Status**: Ensure NLP Worker is running
2. **Verify Dependencies**: Run `make install-clean` in nlp_worker directory
3. **Check Logs**: Look for error messages in service output
4. **Test Connectivity**: Verify ports 5003, 3003, and 8003 are accessible

---

**🎉 Happy Testing!** The simulator will help you verify that your NLP Worker service is working correctly and ready for production use.
