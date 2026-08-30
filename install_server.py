import http.server
import os
import cgi

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
            with open('signed.ipa', 'wb') as f:
                f.write(body)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'IPA uploaded')
        else:
            self.send_response(404)
            self.end_headers()

port = int(os.environ.get('PORT', 10000))
server = http.server.HTTPServer(('0.0.0.0', port), InstallHandler)
print(f"SignBeast Server running on port {port}")
server.serve_forever()
