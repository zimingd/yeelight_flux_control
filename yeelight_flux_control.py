#!/usr/bin/python
import socket
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qsl

YEELIGHT_IPS = []  # Add the IP addresses of your Yeelights to this list:
TRANSITION_DURATION_MS = 2000
TRANSITION_TYPE = "smooth"

YEELIGHT_CONTROL_PORT = 55443  # This is defined by Yeelight's API. Don't change
FLUX_LISTEN_PORT = 42069


class FluxColorTempHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # respond to f.lux so it doesn't keep trying to resend
        self.send_response(200)
        self.end_headers()

        parsed_path = urlparse(self.path)
        params = dict(parse_qsl(parsed_path.query))

        color_temp = int(params['ct'])
        brightness = int(round(float(params['bri']) * 100))  # flux's brightness levels are a bit low, maybe adjust?

        print(f"changing brightness to: {brightness}")
        brightness_change_msg = f'{{"id": 1, "method": "set_bright", "params":[{brightness},"{TRANSITION_TYPE}",{TRANSITION_DURATION_MS}]}}\r\n'

        print(f"changing color temp to: {color_temp}")
        color_temp_change_msg = f'{{"id": 1, "method": "set_ct_abx", "params":[{color_temp},"{TRANSITION_TYPE}",{TRANSITION_DURATION_MS}]}}\r\n'

        for ip in YEELIGHT_IPS:
            #no reason to keep socket alive since updates should be infrequent
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.connect((ip, YEELIGHT_CONTROL_PORT))
                s.send(brightness_change_msg.encode())
                s.send(color_temp_change_msg.encode())


print(f"Configure f.lux to post to: http://localhost:{FLUX_LISTEN_PORT}")
server = HTTPServer(('', FLUX_LISTEN_PORT), FluxColorTempHTTPRequestHandler)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
server.server_close()
