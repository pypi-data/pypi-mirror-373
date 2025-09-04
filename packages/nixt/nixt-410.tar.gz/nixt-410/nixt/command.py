# This file is placed in the Public Domain.


"commands"


import hashlib
import inspect
import importlib
import importlib.util
import logging
import os
import sys
import threading
import _thread


from .clients import NAME, Fleet
from .runtime import launch


loadlock = threading.RLock()


class Mods:

    loaded = []
    md5s   = {}
    ignore = ""
    path   = os.path.dirname(__file__)
    path   = os.path.join(path, "modules")
    pname  = f"{NAME}.modules"


class Commands:

    cmds  = {}
    names = {}

    @staticmethod
    def add(func, module=None) -> None:
        Commands.cmds[func.__name__] = func
        if module:
            Commands.names[func.__name__] = module.__name__.split(".")[-1]

    @staticmethod
    def get(cmd):
        func = Commands.cmds.get(cmd, None)
        if not func:
            name = Commands.names.get(cmd, None)
            if not name:
                return
            module = mod(name)
            if module:
                scan(module)
                func = Commands.cmds.get(cmd)
        return func


def command(evt):
    parse(evt)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        Fleet.display(evt)
    evt.ready()


def inits(names):
    modz = []
    for name in spl(names):
        try:
            module = mod(name)
            if not module:
                continue
            if "init" in dir(module):
                thr = launch(module.init)
                modz.append((module, thr))
        except Exception as ex:
            logging.exception(ex)
            _thread.interrupt_main()
    return modz


def scan(module):
    for key, cmdz in inspect.getmembers(module, inspect.isfunction):
        if key.startswith("cb"):
            continue
        if 'event' in cmdz.__code__.co_varnames:
            Commands.add(cmdz, module)


def table():
    tbl = mod("tbl")
    names = getattr(tbl, "NAMES", None)
    if names:
        Commands.names.update(names)


"modules"


def md5sum(path):
    with open(path, "r", encoding="utf-8") as file:
        txt = file.read().encode("utf-8")
        return hashlib.md5(txt).hexdigest()


def mod(name, debug=False):
    with loadlock:
        module = None
        mname = f"{Mods.pname}.{name}"
        module = sys.modules.get(mname, None)
        if not module:
            pth = os.path.join(Mods.path, f"{name}.py")
            if not os.path.exists(pth):
                return None
            if md5sum(pth) == (hash or Mods.md5s.get(name, None)):
                logging.error(f"md5 doesn't match on {pth}")
            spec = importlib.util.spec_from_file_location(mname, pth)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mname] = module
            spec.loader.exec_module(module)
            Mods.loaded.append(module.__name__.split(".")[-1])
        if debug:
            module.DEBUG = True
        return module


def mods(names=""):
    res = []
    for nme in sorted(modules(Mods.path)):
        if names and nme not in spl(names):
            continue
        module = mod(nme)
        if not mod:
            continue
        res.append(module)
    return res


def modules(mdir=""):
    return sorted([
            x[:-3] for x in os.listdir(mdir or Mods.path)
            if x.endswith(".py") and not x.startswith("__") and
            x[:-3] not in Mods.ignore
           ])


def sums(md5):
    pth = os.path.join(Mods.path, "tbl.py")
    if os.path.exists(pth) and (not md5 or (md5sum(pth) == md5)):
        try:
            module = mod("tbl")
        except FileNotFoundError:
            return {}
        sms =  getattr(module, "MD5", None)
        if sms:
            Mods.md5s.update(sms)
            return True
    return False


"utilities"


def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    yea = 365 * 24 * 60 * 60
    week = 7 * 24 * 60 * 60
    nday = 24 * 60 * 60
    hour = 60 * 60
    minute = 60
    yeas = int(nsec / yea)
    nsec -= yeas * yea
    weeks = int(nsec / week)
    nsec -= weeks * week
    nrdays = int(nsec / nday)
    nsec -= nrdays * nday
    hours = int(nsec / hour)
    nsec -= hours * hour
    minutes = int(nsec / minute)
    nsec -= int(minute * minutes)
    sec = int(nsec)
    if yeas:
        txt += f"{yeas}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def parse(obj, txt=None):
    if txt is None:
        if "txt" in dir(obj):
            txt = obj.txt
        else:
            txt = ""
    args = []
    obj.args   = []
    obj.cmd    = ""
    obj.gets   = {}
    obj.index  = None
    obj.mod    = ""
    obj.opts   = ""
    obj.result = {}
    obj.sets   = {}
    obj.silent = {}
    obj.txt    = txt or ""
    obj.otxt   = obj.txt
    _nr = -1
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "-=" in spli:
            key, value = spli.split("-=", maxsplit=1)
            obj.silent[key] = value
            obj.gets[key] = value
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            obj.gets[key] = value
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            obj.sets[key] = value
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""


def spl(txt):
    try:
        result = txt.split(",")
    except (TypeError, ValueError):
        result = [
            txt,
        ]
    return [x for x in result if x]


"interface"


def __dir__():
    return (
        'Commands',
        'command',
        'elapsed',
        'inits',
        'mod',
        'mods',
        'modules',
        'parse',
        'scan',
        'spl',
        'table'
    )
