import http.server
import os
import subprocess
import json

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

            app_name = self.headers.get('X-App-Name', 'App')

            manifest = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>items</key>
    <array>
        <dict>
            <key>assets</key>
            <array>
                <dict>
                    <key>kind</key>
                    <string>software-package</string>
                    <key>url</key>
                    <string>https://signbeast.onrender.com/signed.ipa</string>
                </dict>
            </array>
            <key>metadata</key>
            <dict>
                <key>bundle-identifier</key>
                <string>com.{app_name.lower()}.app</string>
                <key>bundle-version</key>
                <string>1.0</string>
                <key>kind</key>
                <string>software</string>
                <key>title</key>
                <string>{app_name}</string>
            </dict>
        </dict>
    </array>
</dict>
</plist>
'''
            with open('manifest.plist', 'w') as f:
                f.write(manifest)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'IPA uploaded')
        elif self.path.endswith('.p12'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            with open('cert.p12', 'wb') as f:
                f.write(body)
            self.send_response(200)
            self.end_headers()
        elif self.path.endswith('.mobileprovision'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            with open('cert.mobileprovision', 'wb') as f:
                f.write(body)
            self.send_response(200)
            self.end_headers()
        elif self.path.startswith('/sign'):
            self.do_SIGN()
        else:
            self.send_response(404)
            self.end_headers()

    def do_SIGN(self):
        os.chmod('zsign', 0o755)

        if not os.path.exists('input.ipa'):
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No IPA uploaded"}).encode())
            return

        if not os.path.exists('cert.p12') or not os.path.exists('cert.mobileprovision'):
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No certificate uploaded"}).encode())
            return

        try:
            password = ""
            if os.path.exists('password.txt'):
                with open('password.txt', 'r') as f:
                    password = f.read().strip()

            cmd = ['./zsign', '-k', 'cert.p12', '-p', password, '-m', 'cert.mobileprovision', '-o', 'signed.ipa', 'input.ipa']
            result = subprocess.run(cmd, capture_output=True, text=True)

            if not os.path.exists('signed.ipa'):
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Signing failed: " + result.stderr}).encode())
                return

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status":"signed"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_POST(self):
        if self.path.startswith('/password'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            with open('password.txt', 'w') as f:
                f.write(body)
            self.send_response(200)
            self.end_headers()

port = int(os.environ.get('PORT', 10000))
os.chmod('zsign', 0o755)
server = http.server.HTTPServer(('0.0.0.0', port), InstallHandler)
print(f"SignBeast Server running on port {port}")
server.serve_forever()
