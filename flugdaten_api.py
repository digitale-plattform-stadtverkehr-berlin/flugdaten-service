from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import sys
import json
import requests
import datetime
import time
import pytz
import os

TIMEZONE = pytz.timezone("Europe/Berlin")

URL = os.environ.get('DOWNLOAD_URL')
USER = os.environ.get('DOWNLOAD_USER')
PW = os.environ.get('DOWNLOAD_PW')
AUTH = (USER,PW)

HOST_NAME = os.environ.get('HOST')
PORT_NUMBER = int(os.environ.get('PORT'))

LOG_LEVEL = os.environ.get('LOG_LEVEL')
TRACE = 'TRACE'
DEBUG = 'DEBUG'
INFO = 'INFO'

def trace(message):
    if LOG_LEVEL==TRACE:
        print(message)
def debug(message):
    if LOG_LEVEL==DEBUG:
        print(message)
def info(message):
    if LOG_LEVEL==INFO:
        print(message)

class Server(BaseHTTPRequestHandler):
    def do_HEAD(self):
        return

    def do_GET(self):
        self.respond()

    def do_POST(self):
        return

    def handle_http(self, status, content_type):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        content = self.get_data()
        return bytes(json.dumps(content, indent=4, sort_keys=False, ensure_ascii=False), "UTF-8")

    def respond(self):
        content = self.handle_http(200, 'application/json')
        self.wfile.write(content)

    def get_data(self):
        if 'last_update' not in self.state or (self.state['last_update']+ datetime.timedelta(minutes=5) < datetime.datetime.now()):
            self.load_data()
        return self.data

    def load_data(self):
        info('Load Data')
        r = requests.get(URL, auth=AUTH)
        debug('HTTP-Status: '+str(r.status_code))
        if (r.status_code == 200):
            response = r.text.split('\n')
            data  = {'departures': [], 'arrivals': []}
            now = TIMEZONE.localize(datetime.datetime.now())
            limitTime = ((now.hour+12)%24)*100+now.minute
            limitNextDay = now.hour > 12
            debug(limitTime)
            lastTime = None
            if limitNextDay:
                lastTime=1000
            nextDay = False
            block = 0
            for line in response:
                if line == '{Block 1}':
                    trace('Start Block 1')
                    block = 1
                elif line == '{Block 2}':
                    trace('Start Block 2')
                    block = 2
                elif line == '{Ende Block}':
                    trace('End Block')
                    block = 0
                    lastTime = None
                    nextDay = False
                elif block == 1:
                    trace('Departure')
                    entries = line.split('|')
                    if len(entries) >= 7 and entries[0] != '':
                        if lastTime != None and lastTime > int(entries[2]):
                            nextDay = True
                        if (limitNextDay and (not nextDay or int(entries[2]) <= limitTime)) or (not limitNextDay and not nextDay and int(entries[2]) <= limitTime):
                            planned = entries[2][0:2]+':'+entries[2][2:4]
                            estimated = ""
                            if len(entries[3]) > 0:
                                estimated = entries[3][0:2]+':'+entries[3][2:4]
                            terminal = entries[6]
                            if len(terminal) > 0:
                                terminal = 'T'+terminal
                            entry = {
                                'flight': entries[0],
                                'destination': entries[1].strip(),
                                'planned': planned,
                                'estimated': estimated,
                                'status': entries[4],
                                'checkin': entries[5].strip(),
                                'terminal': terminal
                            }
                            data['departures'].append(entry)
                        lastTime = int(entries[2])
                elif block == 2:
                    trace('Arrival')
                    entries = line.split('|')
                    if len(entries) >= 7 and entries[0] != '':
                        if lastTime != None and lastTime > int(entries[2]):
                            nextDay = True
                        if (limitNextDay and ((not nextDay) or int(entries[2]) <= limitTime)) or ((not limitNextDay) and (not nextDay) and int(entries[2]) <= limitTime):
                            if lastTime != None and lastTime > int(entries[2]):
                                nextDay = True
                        if (limitNextDay and (not nextDay or int(entries[2]) <= limitTime)) or (not limitNextDay and not nextDay and int(entries[2]) <= limitTime):
                            planned = entries[2][0:2]+':'+entries[2][2:4]
                            estimated = ""
                            if len(entries[3]) > 0:
                                estimated = entries[3][0:2]+':'+entries[3][2:4]
                            terminal = entries[5]
                            if len(terminal) > 0:
                                terminal = 'T'+terminal
                            entry = {
                                'flight': entries[0],
                                'origin': entries[1].strip(),
                                'planned': planned,
                                'estimated': estimated,
                                'status': entries[4],
                                'terminal': terminal
                            }
                            data['arrivals'].append(entry)
                        lastTime = int(entries[2])

            debug('Departures: '+str((len(data['departures']))))
            debug('Arrivals: '+str((len(data['arrivals']))))
            if len(data['departures']) > 0:
                self.data['departures'] = data['departures']
            if len(data['arrivals']) > 0:
                self.data['arrivals'] = data['arrivals']
            self.state['last_update'] = datetime.datetime.now()

    state = {}
    data = {'departures': [], 'arrivals': []}



if __name__ == '__main__':
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), Server)
    print(time.asctime(), 'Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))
