# This file is placed in the Public Domain.


"rich site syndicate"


import html
import html.parser
import http.client
import os
import re
import time
import urllib
import urllib.parse
import urllib.request
import uuid
import _thread


from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode


from ..clients import Fleet
from ..command import elapsed, spl
from ..objects import Object, fmt, update
from ..persist import find, fntime, getpath, last, write
from ..runtime import Repeater, launch, rlog


def init():
    fetcher = Fetcher()
    fetcher.start()
    return fetcher


DEBUG = False


fetchlock = _thread.allocate_lock()
importlock = _thread.allocate_lock()
errors = []
skipped = []


class Feed:

    def __init__(self):
        self.link = ""
        self.name = ""


class Rss:

    def __init__(self):
        self.display_list = "title,link,author"
        self.insertid = None
        self.name = ""
        self.rss = ""


class Urls:

    pass


class Fetcher(Object):

    def __init__(self):
        self.dosave = False
        self.seen = Urls()
        self.seenfn = None

    @staticmethod
    def display(obj):
        displaylist = ""
        result = ""
        try:
            displaylist = obj.display_list or "title,link"
        except AttributeError:
            displaylist = "title,link,author"
        for key in displaylist.split(","):
            if not key:
                continue
            data = getattr(obj, key, None)
            if not data:
                continue
            data = data.replace("\n", " ")
            data = striphtml(data.rstrip())
            data = unescape(data)
            result += data.rstrip()
            result += " - "
        return result[:-2].rstrip()

    def fetch(self, feed, silent=False):
        with fetchlock:
            result = []
            seen = getattr(self.seen, feed.rss, [])
            urls = []
            counter = 0
            for obj in reversed(getfeed(feed.rss, feed.display_list)):
                counter += 1
                fed = Feed()
                update(fed, obj)
                update(fed, feed)
                url = urllib.parse.urlparse(fed.link)
                if url.path and not url.path == "/":
                    uurl = f"{url.scheme}://{url.netloc}/{url.path}"
                else:
                    uurl = fed.link
                urls.append(uurl)
                if uurl in seen:
                    continue
                if self.dosave:
                    write(fed)
                result.append(fed)
            setattr(self.seen, feed.rss, urls)
            if not self.seenfn:
                self.seenfn = getpath(self.seen)
            write(self.seen, self.seenfn)
        if silent:
            return counter
        txt = ""
        feedname = getattr(feed, "name", None)
        if feedname:
            txt = f"[{feedname}] "
        for obj in result:
            txt2 = txt + self.display(obj)
            for bot in Fleet.all():
                bot.announce(txt2)
        return counter

    def run(self, silent=False):
        thrs = []
        for _fn, feed in find("rss"):
            thrs.append(launch(self.fetch, feed, silent))
        return thrs

    def start(self, repeat=True):
        self.seenfn = last(self.seen)
        if repeat:
            repeater = Repeater(300.0, self.run)
            repeater.start()


class Parser:

    @staticmethod
    def getitem(line, item):
        lne = ""
        index1 = line.find(f"<{item}>")
        if index1 == -1:
            return lne
        index1 += len(item) + 2
        index2 = line.find(f"</{item}>", index1)
        if index2 == -1:
            return lne
        lne = line[index1:index2]
        lne = cdata(lne)
        return lne.strip()

    @staticmethod
    def getitems(text, token):
        index = 0
        result = []
        stop = False
        while not stop:
            index1 = text.find(f"<{token}", index)
            if index1 == -1:
                break
            index1 += len(token) + 2
            index2 = text.find(f"</{token}>", index1)
            if index2 == -1:
                break
            lne = text[index1:index2]
            result.append(lne)
            index = index2
        return result

    @staticmethod
    def parse(txt, toke="item", items="title,link"):
        result = []
        for line in Parser.getitems(txt, toke):
            line = line.strip()
            obj = Object()
            for itm in spl(items):
                val = Parser.getitem(line, itm)
                if val:
                    val = unescape(val.strip())
                    val = val.replace("\n", "")
                    val = striphtml(val)
                    setattr(obj, itm, val)
            result.append(obj)
        return result


"OPML"


class OPML:

    @staticmethod
    def getnames(line):
        return [x.split('="')[0] for x in line.split()]

    @staticmethod
    def getvalue(line, attr):
        lne = ""
        index1 = line.find(f'{attr}="')
        if index1 == -1:
            return lne
        index1 += len(attr) + 2
        index2 = line.find('"', index1)
        if index2 == -1:
            index2 = line.find("/>", index1)
        if index2 == -1:
            return lne
        lne = line[index1:index2]
        if "CDATA" in lne:
            lne = lne.replace("![CDATA[", "")
            lne = lne.replace("]]", "")
            # lne = lne[1:-1]
        return lne

    @staticmethod
    def getattrs(line, token):
        index = 0
        result = []
        stop = False
        while not stop:
            index1 = line.find(f"<{token} ", index)
            if index1 == -1:
                return result
            index1 += len(token) + 2
            index2 = line.find("/>", index1)
            if index2 == -1:
                return result
            result.append(line[index1:index2])
            index = index2
        return result

    @staticmethod
    def parse(txt, toke="outline", itemz=None):
        if itemz is None:
            itemz = ",".join(OPML.getnames(txt))
        result = []
        for attrz in OPML.getattrs(txt, toke):
            if not attrz:
                continue
            obj = Object()
            for itm in spl(itemz):
                if itm == "link":
                    itm = "href"
                val = OPML.getvalue(attrz, itm)
                if not val:
                    continue
                if itm == "href":
                    itm = "link"
                setattr(obj, itm, val.strip())
            result.append(obj)
        return result


"utilities"


def attrs(obj, txt):
    update(obj, OPML.parse(txt))


def cdata(line):
    if "CDATA" in line:
        lne = line.replace("![CDATA[", "")
        lne = lne.replace("]]", "")
        lne = lne[1:-1]
        return lne
    return line


def getfeed(url, items):
    result = [Object(), Object()]
    if DEBUG or url in errors:
        return result
    try:
        rest = geturl(url)
    except (http.client.HTTPException, ValueError, HTTPError, URLError) as ex:
        rlog("error", f"{url} {ex}")
        errors.append(url)
        return result
    if rest:
        if "link" not in items:
            items += ",link"
        if url.endswith("atom"):
            result = Parser.parse(str(rest.data, "utf-8"), "entry", items) or []
        else:
            result = Parser.parse(str(rest.data, "utf-8"), "item", items) or []
    return result


def gettinyurl(url):
    postarray = [
        ("submit", "submit"),
        ("url", url),
    ]
    postdata = urlencode(postarray, quote_via=quote_plus)
    req = urllib.request.Request(
        "http://tinyurl.com/create.php", data=bytes(postdata, "UTF-8")
    )
    req.add_header("User-agent", useragent("rss fetcher"))
    with urllib.request.urlopen(req) as htm:  # nosec
        for txt in htm.readlines():
            line = txt.decode("UTF-8").strip()
            i = re.search('data-clipboard-text="(.*?)"', line, re.M)
            if i:
                return i.groups()
    return []


def geturl(url):
    url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
    req = urllib.request.Request(str(url))
    req.add_header("User-agent", useragent("rss fetcher"))
    with urllib.request.urlopen(req) as response:  # nosec
        response.data = response.read()
        return response


def shortid():
    return str(uuid.uuid4())[:8]


def striphtml(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def unescape(text):
    txt = re.sub(r"\s+", " ", text)
    return html.unescape(txt)


def useragent(txt):
    return "Mozilla/5.0 (X11; Linux x86_64) " + txt


"commands"


def dpl(event):
    if len(event.args) < 2:
        event.reply("dpl <stringinurl> <item1,item2>")
        return
    setter = {"display_list": event.args[1]}
    for fnm, feed in find("rss", {"rss": event.args[0]}):
        if feed:
            update(feed, setter)
            write(feed, fnm)
    event.done()


def exp(event):
    with importlock:
        event.reply(TEMPLATE)
        nrs = 0
        for _fn, ooo in find("rss"):
            nrs += 1
            obj = Rss()
            update(obj, ooo)
            name = f"url{nrs}"
            txt = f'<outline name="{name}" display_list="{obj.display_list}" xmlUrl="{obj.rss}"/>'
            event.reply(" " * 12 + txt)
        event.reply(" " * 8 + "</outline>")
        event.reply("    <body>")
        event.reply("</opml>")


def imp(event):
    if not event.args:
        event.reply("imp <filename>")
        return
    fnm = event.args[0]
    if not os.path.exists(fnm):
        event.reply(f"no {fnm} file found.")
        return
    with open(fnm, "r", encoding="utf-8") as file:
        txt = file.read()
    prs = OPML()
    nrs = 0
    nrskip = 0
    insertid = shortid()
    with importlock:
        for obj in prs.parse(txt, "outline", "name,display_list,xmlUrl"):
            url = obj.xmlUrl
            if url in skipped:
                continue
            if not url.startswith("http"):
                continue
            has = list(find("rss", {"rss": url}, matching=True))
            if has:
                skipped.append(url)
                nrskip += 1
                continue
            feed = Rss()
            update(feed, obj)
            feed.rss = obj.xmlUrl
            feed.insertid = insertid
            write(feed)
            nrs += 1
    if nrskip:
        event.reply(f"skipped {nrskip} urls.")
    if nrs:
        event.reply(f"added {nrs} urls.")


def nme(event):
    if len(event.args) != 2:
        event.reply("nme <stringinurl> <name>")
        return
    selector = {"rss": event.args[0]}
    for fnm, fed in find("rss", selector):
        feed = Rss()
        update(feed, fed)
        if feed:
            feed.name = str(event.args[1])
            write(feed, fnm)
    event.done()


def rem(event):
    if len(event.args) != 1:
        event.reply("rem <stringinurl>")
        return
    for fnm, fed in find("rss"):
        feed = Rss()
        update(feed, fed)
        if event.args[0] not in feed.rss:
            continue
        if feed:
            feed.__deleted__ = True
            write(feed)
            event.done()
            break


def res(event):
    if len(event.args) != 1:
        event.reply("res <stringinurl>")
        return
    for fnm, fed in find("rss", deleted=True):
        feed = Rss()
        update(feed, fed)
        if event.args[0] not in feed.rss:
            continue
        if feed:
            feed.__deleted__ = False
            write(feed, fnm)
    event.done()


def rss(event):
    if not event.rest:
        nrs = 0
        for fnm, fed in find("rss"):
            nrs += 1
            elp = elapsed(time.time() - fntime(fnm))
            txt = fmt(fed)
            event.reply(f"{nrs} {txt} {elp}")
        if not nrs:
            event.reply("no feed found.")
        return
    url = event.args[0]
    if "http://" not in url and "https://" not in url:
        event.reply("i need an url")
        return
    for fnm, result in find("rss", {"rss": url}):
        if result:
            event.reply(f"{url} is known")
            return
    feed = Rss()
    feed.rss = event.args[0]
    write(feed)
    event.done()


def syn(event):
    if DEBUG:
        return
    fetcher = Fetcher()
    fetcher.start(False)
    thrs = fetcher.run(True)
    nrs = 0
    for thr in thrs:
        thr.join()
        nrs += 1
    event.reply(f"{nrs} feeds synced")


TEMPLATE = """<opml version="1.0">
    <head>
        <title>OPML</title>
    </head>
    <body>
        <outline title="opml" text="rss feeds">"""
