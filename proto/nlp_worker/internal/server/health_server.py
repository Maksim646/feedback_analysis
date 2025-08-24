import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from typing import Optional

from internal.metrics.nlp_worker_metrics import NlpWorkerMetrics


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks"""
    
    def __init__(self, *args, metrics: Optional[NlpWorkerMetrics] = None, **kwargs):
        self.metrics = metrics
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests for health checks"""
        if self.path == '/ready':
            self._handle_readiness()
        elif self.path == '/live':
            self._handle_liveness()
        elif self.path == '/metrics':
            self._handle_metrics()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def _handle_readiness(self):
        """Handle readiness probe"""
        try:
            # Check if service is ready to receive traffic
            # For now, always return ready
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "ready",
                "service": "nlp_worker_service"
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "not_ready",
                "error": str(e),
                "service": "nlp_worker_service"
            }
            self.wfile.write(json.dumps(response).encode())
    
    def _handle_liveness(self):
        """Handle liveness probe"""
        try:
            # Check if service is alive and functioning
            # For now, always return alive
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "alive",
                "service": "nlp_worker_service"
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "not_alive",
                "error": str(e),
                "service": "nlp_worker_service"
            }
            self.wfile.write(json.dumps(response).encode())
    
    def _handle_metrics(self):
        """Handle metrics endpoint"""
        if self.metrics:
            metrics_summary = self.metrics.get_metrics_summary()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            self.wfile.write(json.dumps(metrics_summary, indent=2).encode())
        else:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {"error": "Metrics not available"}
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Override to use our logger instead of stderr"""
        pass


def start_health_server(port: int, metrics: Optional[NlpWorkerMetrics] = None, logger: Optional[logging.Logger] = None):
    """Start the health check server in a separate thread"""
    
    def run_server():
        try:
            # Create custom handler class with metrics
            class CustomHandler(HealthCheckHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, metrics=metrics, **kwargs)
            
            server = HTTPServer(('', port), CustomHandler)
            if logger:
                logger.info(f"Health check server started on port {port}")
            server.serve_forever()
            
        except Exception as e:
            if logger:
                logger.error(f"Health check server failed: {e}")
    
    # Start server in background thread
    health_thread = threading.Thread(target=run_server, daemon=True)
    health_thread.start()
    
    return health_thread
