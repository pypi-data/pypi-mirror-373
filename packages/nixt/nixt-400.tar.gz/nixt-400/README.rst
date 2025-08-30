N I X B O T
===========


**NAME**


|
| ``nixt`` - NIXT
|


**SYNOPSIS**


|
| ``nixt <cmd> [key=val] [key==val]``
| ``nixt -cvaw [init=mod1,mod2]``
| ``nixt -d`` 
| ``nixt -s``
|

**DESCRIPTION**


``NIXT`` has all you need to program a unix cli program, such as disk
perisistence for configuration files, event handler to handle the
client/server connection, deferred exception handling to not crash
on an error, etc.

``NIXT`` contains python3 code to program objects in a functional way.
it provides an "clean namespace" Object class that only has dunder
methods, so the namespace is not cluttered with method names. This
makes storing and reading to/from json possible.

``NIXT`` is a python3 IRC bot, it can connect to IRC, fetch and
display RSS feeds, take todo notes, keep a shopping list and log
text. You can run it under systemd for 24/7 presence in a IRC channel.


``NIXBOT`` is Public Domain.


**INSTALL**


installation is done with pipx

|
| ``$ pipx install nixt``
| ``$ pipx ensurepath``
|
| <new terminal>
|
| ``$ nixt srv > nixt.service``
| ``$ sudo mv nixt.service /etc/systemd/system/``
| ``$ sudo systemctl enable nixt --now``
|
| joins ``#nixt`` on localhost
|


**USAGE**


use ``nixt`` to control the program, default it does nothing

|
| ``$ nixt``
| ``$``
|

see list of commands

|
| ``$ nixt cmd``
| ``cfg,cmd,dne,dpl,err,exp,imp,log,mod,mre,nme,``
| ``pwd,rem,req,res,rss,srv,syn,tdo,thr,upt``
|

start console

|
| ``$ nixt -c``
|

start console and run irc and rss clients

|
| ``$ nixt -c init=irc,rss``
|

list available modules

|
| ``$ nixt mod``
| ``err,flt,fnd,irc,llm,log,mbx,mdl,mod,req,rss,``
| ``rst,slg,tdo,thr,tmr,udp,upt``
|

start daemon

|
| ``$ nixt -d``
| ``$``
|

start service

|
| ``$ nixt -s``
| ``<runs until ctrl-c>``
|


**COMMANDS**


here is a list of available commands

|
| ``cfg`` - irc configuration
| ``cmd`` - commands
| ``dpl`` - sets display items
| ``err`` - show errors
| ``exp`` - export opml (stdout)
| ``imp`` - import opml
| ``log`` - log text
| ``mre`` - display cached output
| ``pwd`` - sasl nickserv name/pass
| ``rem`` - removes a rss feed
| ``res`` - restore deleted feeds
| ``req`` - reconsider
| ``rss`` - add a feed
| ``syn`` - sync rss feeds
| ``tdo`` - add todo item
| ``thr`` - show running threads
| ``upt`` - show uptime
|

**CONFIGURATION**


irc

|
| ``$ nixt cfg server=<server>``
| ``$ nixt cfg channel=<channel>``
| ``$ nixt cfg nick=<nick>``
|

sasl

|
| ``$ nixt pwd <nsnick> <nspass>``
| ``$ nixt cfg password=<frompwd>``
|

rss

|
| ``$ nixt rss <url>``
| ``$ nixt dpl <url> <item1,item2>``
| ``$ nixt rem <url>``
| ``$ nixt nme <url> <name>``
|

opml

|
| ``$ nixt exp``
| ``$ nixt imp <filename>``
|


**PROGRAMMING**


``nixt`` has it's modules in the package, so edit a file in nixt/modules/<name>.py
and add the following for ``hello world``

::

    def hello(event):
        event.reply("hello world !!")


``nixt`` uses loading on demand of modules and has a ``tbl`` command to
generate a table for this.


|
| ``$ nixt tbl > nixt/modules/tbl.py``
|

a md5sum can be added to verify the modules md5sums are matching.

|
| ``$ nixt md5``
|

put this value in nixt/modules/__init__.py and ``nixt`` can execute the ``hello``
command now.

|
| ``$ nixt hello``
| ``hello world !!``
|

Commands run in their own thread and the program borks on exit, output gets
flushed on print so exceptions appear in the systemd logs. Modules can contain
your own written python3 code, see the nixt/modules directory for examples.


**FILES**

|
| ``~/.nixt``
| ``~/.local/bin/nixt``
| ``~/.local/pipx/venvs/nixt/*``
|

**AUTHOR**

|
| ``Bart Thate`` <``nixtniet@gmail.com``>
|

**COPYRIGHT**

|
| ``NIXT`` is Public Domain.
|
