# This file is placed in the Public Domain.


"web"


import logging
import os
import sys
import time


from http.server import HTTPServer, BaseHTTPRequestHandler


from ..objects import Object
from ..runtime import launch, rlog


DEBUG = False


def init():
    try:
        server = HTTP((Cfg.hostname, int(Cfg.port)), HTTPHandler)
        server.start()
        rlog("debug", f"web at http://{Cfg.hostname}:{Cfg.port}")
        return server
    except OSError as ex:
        rlog("debug", f"web abort {ex}")


class Cfg:

    hostname = "localhost"
    port     = 8000


class HTTP(HTTPServer, Object):

    daemon_thread = True
    allow_reuse_address = True

    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        Object.__init__(self)
        self.host = args[0]
        self._starttime = time.time()
        self._last = time.time()
        self._status = "start"

    def exit(self):
        time.sleep(0.2)
        self._status = ""
        self.shutdown()

    def start(self):
        launch(self.serve_forever)
        self._status = "ok"

    def request(self):
        self._last = time.time()

    def error(self, _request, _addr):
        exctype, excvalue, _trb = sys.exc_info()
        exc = exctype(excvalue)
        logging.exception(exc)


class HTTPHandler(BaseHTTPRequestHandler):

    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self._size = 0
        self._ip = self.client_address[0]

    def raw(self, data):
        self.wfile.write(data)

    def send(self, txt):
        self.wfile.write(bytes(txt, encoding="utf-8"))
        self.wfile.flush()

    def write_header(self, htype='text/plain', size=None):
        self.send_response(200)
        #self.send_header('Content-type', '%s; charset=%s ' % (htype, "utf-8"))
        self.send_header('Content-type', '%s;')
        if size is not None:
            self.send_header('Content-length', size)
        self.send_header('Server', "1")
        self.end_headers()

    def log(self, code):
        pass

    def do_GET(self):
        if "favicon" in self.path:
            return
        if DEBUG:
            return
        if self.path == "/":
            self.path = "/index.html"
        self.path = "html" + os.sep + self.path
        if not os.path.exists(self.path):
            self.write_header("text/html")
            self.send_response(404)
            self.end_headers()
            return
        if "_images" in self.path:
            try:
                with open(self.path, "rb") as file:
                    img = file.read()
                    file.close()
                ext = self.path[-3]
                self.write_header(f"image/{ext}", len(img))
                self.raw(img)
            except (TypeError, FileNotFoundError, IsADirectoryError):
                self.send_response(404)
                self.end_headers()
            return
        try:
            with open(self.path, "r", encoding="utf-8", errors="ignore") as file:
                txt = file.read()
                file.close()
            self.write_header("text/html")
            self.send(html2(txt))
        except (TypeError, FileNotFoundError, IsADirectoryError):
            self.send_response(404)
            self.end_headers()


def html2(txt):
    return """<!doctype html>
<html>
   %s
</html>
""" % txt
