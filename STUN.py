import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.flushall()
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        if self.path == '/users':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            keys = r.keys('*')
            data = {'users' : [key.decode('utf-8')for key in keys]}
            json_data = json.dumps(data)
            self.wfile.write(json_data.encode('utf-8'))
        elif self.path.split('?')[0] == '/user':
            # Handle saving data logic here
            id = query_params['id']
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = {'port': r.get(id[0]).decode('utf-8')}
            json_data = json.dumps(data)
            self.wfile.write(json_data.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])

        body = self.rfile.read(content_length)

        # form_data = parse_qs(body.decode())
        if self.path == '/signup':
            data = json.loads(body)
            username = data['username']
            ip = data['ip']
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            data = json.loads(body.decode())
            print(data['username'])
            r.set(data['username'], data['port'])
            self.wfile.write('Done'.encode('utf-8'))
            print('{} was signed up with ip: {}'.format(username, ip))
        else:
            # Send a 404 Not Found response
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 Not Found')


            # Handle the posted data and perform any necessary operations
            # For example, you can parse the data, save it, or process it in some way


def run_server(host, port):
    server_address = (host, port)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    print(f"HTTP server running on {host}:{port}")
    httpd.serve_forever()

# Example usage
if __name__ == "__main__":
    run_server("localhost", 8000)
