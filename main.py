from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import time
import cgi
import json
import os

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
PORT = int(os.getenv('PORT'))

class Server(BaseHTTPRequestHandler):
  def _set_headers(self):
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    self.send_header('Access-Control-Allow-Methods', 'OPTIONS,POST')
    self.end_headers()

  def do_OPTIONS(self):
    self._set_headers()

  def do_POST(self):
    content_type, _ = cgi.parse_header(self.headers.get('Content-Type'))
    print(content_type)

    # refuse to receive non-json content
    if content_type != 'application/json':
      self.send_response(400)
      self.end_headers()
      return

    # read the message and convert it into a python dictionary
    length = int(self.headers.get('content-length'))
    message = json.loads(self.rfile.read(length))

    response = {}

    if (self.path == "/api/access-token"):
      response = self.oauthToken(message["code"])

    if (self.path == "/api/refresh-token"):
      response = self.refreshToken(message["refresh_token"])

    self._set_headers()
    self.wfile.write(json.dumps(response).encode('UTF-8'))

  def oauthToken(self, code):
    url = "https://www.strava.com/oauth/token"
    params = {
      "code": code,
      "client_id": CLIENT_ID,
      "client_secret": CLIENT_SECRET,
      "grant_type": "authorization_code",
    }
    url += "?" + urlencode(params, doseq=True, safe="/")

    request = Request(url, method="POST")

    with urlopen(request) as response:
      body = json.load(response)

    return body

  def refreshToken(self, refreshToken):
      url = "https://www.strava.com/oauth/token"
      params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refreshToken,
      }
      url += "?" + urlencode(params, doseq=True, safe="/")

      request = Request(url, method="POST")

      with urlopen(request) as response:
        body = json.load(response)

      return body

if __name__ == "__main__":
  server = HTTPServer(("", PORT), Server)
  server.serve_forever()
