# This file is placed in the Public Domain.


"REST"


import logging
import os
import sys
import time


from http.server import HTTPServer, BaseHTTPRequestHandler


from ..objects import Object
from ..persist import Workdir, types
from ..runtime import launch, rlog


DEBUG = False


def init():
    try:
        rest = REST((Config.hostname, int(Config.port)), RESTHandler)
        rest.start()
        rlog("debug", f"rest at http://{Config.hostname}:{Config.port}")
        return rest
    except OSError as ex:
        rlog("debug", f"rest abort {ex}")


class Config:

    hostname = "localhost"
    port     = 10102


class REST(HTTPServer, Object):

    allow_reuse_address = True
    daemon_thread = True

    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        Object.__init__(self)
        self.host = args[0]
        self._last = time.time()
        self._starttime = time.time()
        self._status = "start"

    def exit(self):
        self._status = ""
        time.sleep(0.2)
        self.shutdown()

    def start(self):
        self._status = "ok"
        launch(self.serve_forever)

    def request(self):
        self._last = time.time()

    def error(self, _request, _addr):
        exctype, excvalue, _trb = sys.exc_info()
        exc = exctype(excvalue)
        logging.exception(exc)


class RESTHandler(BaseHTTPRequestHandler):

    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self._ip = self.client_address[0]
        self._size = 0

    def send(self, txt):
        self.wfile.write(bytes(txt, "utf-8"))
        self.wfile.flush()

    def write_header(self, htype='text/plain'):
        self.send_response(200)
        self.send_header('Content-type', '%s; charset=%s ' % (htype, "utf-8"))
        self.send_header('Server', "1")
        self.end_headers()

    def do_GET(self):
        if DEBUG:
            return
        if "favicon" in self.path:
            return
        if self.path == "/":
            self.write_header("text/html")
            txt = ""
            for fnm in types():
                txt += f'<a href="http://{Config.hostname}:{Config.port}/{fnm}">{fnm}</a><br>\n'
            self.send(html(txt.strip()))
            return
        fnm = Workdir.wdr + os.sep + "store" + self.path
        fnm = os.path.abspath(fnm)
        if os.path.isdir(fnm):
            self.write_header("text/html")
            txt = ""
            for fnn in os.listdir(fnm):
                filename = self.path  + os.sep + fnn
                txt += f'<a href="http://{Config.hostname}:{Config.port}/{filename}">{filename}</a><br>\n'
            self.send(txt.strip())
            return
        try:
            with open(fnm, "r", encoding="utf-8") as file:
                txt = file.read()
                file.close()
            self.write_header("text/html")
            self.send(html(txt))
        except (TypeError, FileNotFoundError, IsADirectoryError) as ex:
            self.send_response(404)
            logging.exception(ex)
            self.end_headers()

    def log(self, code):
        pass


def html(txt):
    return """<!doctype html>
<html>
   %s
</html>
""" % txt
