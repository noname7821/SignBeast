import http.server
import ssl
import os

class InstallHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.ipa'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', 'attachment; filename="signed.ipa"')
            self.send_header('Content-Length', str(os.path.getsize('signed.ipa')))
            self.end_headers()
            with open('signed.ipa', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path.endswith('.plist'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml')
            self.end_headers()
            with open('manifest.plist', 'rb') as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()

server = http.server.HTTPServer(('0.0.0.0', 8443), InstallHandler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')
server.socket = context.wrap_socket(server.socket, server_side=True)
print("SignBeast Server running on https://0.0.0.0:8443")
server.serve_forever()
