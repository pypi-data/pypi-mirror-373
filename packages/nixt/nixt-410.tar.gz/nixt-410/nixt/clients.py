# This file is placed in the Public Domain.


"clients"


import queue
import threading
import time


from .handler import Handler
from .runtime import launch


NAME = __name__.split(".", maxsplit=1)[0]


class Client(Handler):

    def __init__(self):
        Handler.__init__(self)
        self.olock = threading.RLock()
        Fleet.add(self)

    def announce(self, txt):
        pass

    def display(self, event):
        with self.olock:
            for tme in sorted(event.result):
                self.dosay(event.channel, event.result[tme])

    def dosay(self, channel, txt):
        self.say(channel, txt)

    def raw(self, txt):
        raise NotImplementedError("raw")

    def say(self, channel, txt):
        self.raw(txt)


class Output(Client):

    def __init__(self):
        Client.__init__(self)
        self.olock  = threading.RLock()
        self.oqueue = queue.Queue()
        self.ostop  = threading.Event()

    def display(self, event):
        with self.olock:
            for tme in sorted(event.result):
                self.dosay(event.channel, event.result[tme])

    def dosay(self, channel, txt):
        raise NotImplementedError("dosay")

    def oput(self, event):
        self.oqueue.put(event)

    def output(self):
        while not self.ostop.is_set():
            event = self.oqueue.get()
            if event is None:
                self.oqueue.task_done()
                break
            self.display(event)
            self.oqueue.task_done()

    def start(self):
        self.ostop.clear()
        launch(self.output)
        super().start()

    def stop(self):
        self.ostop.set()
        self.oqueue.put(None)
        super().stop()

    def wait(self):
        self.oqueue.join()


"list of clients"


class Fleet:

    clients = {}

    @staticmethod
    def add(client):
        Fleet.clients[repr(client)] = client

    @staticmethod
    def all():
        return Fleet.clients.values()

    @staticmethod
    def announce(txt):
        for client in Fleet.all():
            client.announce(txt)

    @staticmethod
    def dispatch(evt):
        client = Fleet.get(evt.orig)
        client.put(evt)

    @staticmethod
    def display(evt):
        client = Fleet.get(evt.orig)
        client.display(evt)

    @staticmethod
    def first():
        clt = list(Fleet.all())
        res = None
        if clt:
            res = clt[0]
        return res

    @staticmethod
    def get(orig):
        return Fleet.clients.get(orig, None)

    @staticmethod
    def say(orig, channel, txt):
        client = Fleet.get(orig)
        if client:
            client.say(channel, txt)

    @staticmethod
    def shutdown():
        for client in Fleet.all():
            client.stop()

    @staticmethod
    def wait():
        time.sleep(0.1)
        for client in Fleet.all():
            client.wait()


"interface"


def __dir__():
    return (
        'Client',
        'Output',
        'Fleet'
    )
