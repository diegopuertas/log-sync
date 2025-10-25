#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import threading

# Flag to control the server
running = True

class DaemonHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the daemon"""
    
    def do_GET(self):
        """Handle GET requests - status check"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'running',
            'message': 'Python daemon is alive'
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests - shutdown command"""
        global running
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data) if content_length > 0 else {}
        except json.JSONDecodeError:
            data = {}
        
        # Check if this is a shutdown request
        if self.path == '/shutdown' or data.get('action') == 'shutdown':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'success',
                'message': 'Shutting down daemon...'
            }
            self.wfile.write(json.dumps(response).encode())
            
            print("Received shutdown request via POST. Stopping daemon...")
            running = False
            
            # Shutdown server in a separate thread to allow response to complete
            threading.Thread(target=self.server.shutdown).start()
        else:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'error',
                'message': 'Invalid endpoint. Use POST /shutdown'
            }
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    host = '0.0.0.0'
    port = 8080
    
    server = HTTPServer((host, port), DaemonHandler)
    
    print(f"Python daemon HTTP server started on {host}:{port}")
    print(f"- GET  /       -> Check status")
    print(f"- POST /shutdown -> Stop the daemon")
    print("-" * 50)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("\nDaemon stopped cleanly.")

if __name__ == "__main__":
    main()
