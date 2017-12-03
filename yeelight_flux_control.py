#!/usr/bin/python

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl

import socket
from contextlib import closing

YEELIGHT_IPS = []  # Add the IP addresses of your Yeelights to this list:
YEELIGHT_CONTROL_PORT = 55443  # This is defined by Yeelight's API. Don't change
TRANSITION_DURATION_MS = 30
TRANSITION_TYPE = "sudden"

FLUX_LISTEN_PORT = 42069

# globals to track previous brightness and color temp values since flux POSTs quite often even when there is no change
# There is probably a better way other than using globals. I'm happy to take any suggestions
prev_brightness = 1234
prev_color_temp = 5678


class FluxColorTempHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global prev_color_temp
        global prev_brightness

        # parse '/?ct=123&bri=0.123' after removing the leading '/?'
        params = dict(parse_qsl(self.path[2:]))

        color_temp = int(params['ct'])
        brightness = int(round(float(params['bri']) * 100))  # flux's brightness levels are a bit low, maybe adjust?

        control_messages = []

        if prev_brightness != brightness:
            print(f"changing brightness to: {brightness}")
            control_messages.append(f'{{"id": 1, "method": "set_bright", "params":[{brightness},"{TRANSITION_TYPE}",{TRANSITION_DURATION_MS}]}}\r\n')
            prev_brightness = brightness

        if prev_color_temp != color_temp:
            print(f"changing color temp to: {color_temp}")
            control_messages.append(f'{{"id": 1, "method": "set_ct_abx", "params":[{color_temp},"{TRANSITION_TYPE}",{TRANSITION_DURATION_MS}]}}\r\n')
            prev_color_temp = color_temp

        if control_messages:
            for ip in YEELIGHT_IPS:
                with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                    s.connect((ip, YEELIGHT_CONTROL_PORT))
                    for message in control_messages:
                        s.send(message.encode())


print(f"Configure f.lux to post to: http://localhost:{FLUX_LISTEN_PORT}")
server = HTTPServer(('', FLUX_LISTEN_PORT), FluxColorTempHTTPRequestHandler)
server.serve_forever()
