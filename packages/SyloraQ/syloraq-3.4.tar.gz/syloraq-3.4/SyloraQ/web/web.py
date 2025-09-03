from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse
import threading
from SyloraQ.ChromeController import BrowSentinel

def UrlValidate(url):
    try:
        s=BrowSentinel()
        s.start()
        s.navigate(url)
        s.close()
        return True
    except:return False

ADDEPS = {}

def endpoint(api_name):
    def decorator(func):
        ADDEPS[api_name] = func
        return func
    return decorator

def api(port=8381):
    def ras(port):
        class Handle(BaseHTTPRequestHandler):
            def do_OPTIONS(self):
                self.send_response(204)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Token')
                self.end_headers()
            def do_POST(self):self.handle_request(is_post=True)
            def do_GET(self):self.handle_request(is_post=False)
            def handle_request(self, is_post):
                print("DEBUG: got request", self.command, self.path)
                parsed_path = urlparse(self.path)
                path_parts = parsed_path.path.strip('/').split('/')
                if len(path_parts) != 2 or path_parts[0] != 'api':
                    self.send_response(404)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(b'Invalid path')
                    return
                api_name = path_parts[1]
                handler = ADDEPS.get(api_name)
                if not handler:
                    self.send_response(404)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(b'API not found')
                    return
                body = {}
                if is_post:
                    length = int(self.headers.get('Content-Length', 0))
                    raw = self.rfile.read(length) if length > 0 else b''
                    if 'application/json' in self.headers.get('Content-Type', ''):
                        try:body = json.loads(raw.decode())
                        except json.JSONDecodeError:
                            self.send_response(400)
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            self.wfile.write(b'Invalid JSON')
                            return
                    else:body = raw.decode()
                try:resp = handler(body, self.headers)
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(f'Internal server error: {e}'.encode())
                    return
                resp_bytes = json.dumps(resp).encode() if isinstance(resp, dict) else str(resp).encode()
                ctype = 'application/json' if isinstance(resp, dict) else 'text/plain'
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', ctype)
                self.end_headers()
                self.wfile.write(resp_bytes)
        server_address = ('0.0.0.0', port)
        print(f"Starting API server at http://0.0.0.0:{port}")
        httpd = HTTPServer(server_address, Handle)
        httpd.serve_forever()
    thread = threading.Thread(target=ras, args=(port,), daemon=True)
    thread.start()
    print(f"API server started in background thread on port {port}")
    return thread