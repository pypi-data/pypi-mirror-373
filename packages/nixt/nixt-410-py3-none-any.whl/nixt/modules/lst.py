# This file is been placed in the Public Domain.


"available types"


from ..persist import types


def ls(event):
    event.reply(",".join([x.split(".")[-1].lower() for x in types()]))
