import http.server
import os
import subprocess
import shutil

class InstallHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.ipa'):
            if os.path.exists('signed.ipa'):
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', str(os.path.getsize('signed.ipa')))
                self.end_headers()
                with open('signed.ipa', 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path.endswith('.plist'):
            if os.path.exists('manifest.plist'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/xml')
                self.end_headers()
                with open('manifest.plist', 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'SignBeast Server Running')

    def do_PUT(self):
        if self.path.endswith('.ipa'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            with open('input.ipa', 'wb') as f:
                f.write(body)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"uploaded"}')
        elif self.path.endswith('.p12'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            with open('cert.p12', 'wb') as f:
                f.write(body)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'P12 uploaded')
        elif self.path.endswith('.mobileprovision'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            with open('cert.mobileprovision', 'wb') as f:
                f.write(body)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Provision uploaded')
        elif self.path.startswith('/sign'):
            self.do_SIGN()
        else:
            self.send_response(404)
            self.end_headers()

    def do_SIGN(self):
        try:
            password = ""
            if os.path.exists('password.txt'):
                with open('password.txt', 'r') as f:
                    password = f.read().strip()

            cmd = ['./zsign', '-k', 'cert.p12', '-p', password, '-m', 'cert.mobileprovision', '-o', 'signed.ipa', 'input.ipa']
            result = subprocess.run(cmd, capture_output=True, text=True)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"signed"}')
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_POST(self):
        if self.path.startswith('/password'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            with open('password.txt', 'w') as f:
                f.write(body)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Password saved')

os.chmod('zsign', 0o755)

port = int(os.environ.get('PORT', 10000))
server = http.server.HTTPServer(('0.0.0.0', port), InstallHandler)
print(f"SignBeast Server running on port {port}")
server.serve_forever()
