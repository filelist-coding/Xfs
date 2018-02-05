# rose module aka lingura

import json
import cmd_logger

l_path ="db\\linguri.json"

def AddLingura(Xfs, sock_id, target, nick):
    """Increment lingura count for nick in json."""
    with open(l_path, 'r') as f:
        linguri = json.load(f)

    if (nick in linguri):
        linguri[nick] += 1
    else:
        linguri[nick] = 1
        Xfs.Msg(sock_id, target, nick + ", tocmai ai primit prima ta lingura de lemn, ouch!")
    """Increment total number of linguri used so far."""
    linguri['info_linguri'] += 1

    with open(l_path, 'w') as f:
        json.dump(linguri, f)

def ShowLingura(Xfs, sock_id, target, in_nick):
    """Grab lingura count from jason and show on channel."""
    with open(l_path, 'r') as f:
        linguri = json.load(f)

    if (in_nick in linguri):
        Xfs.Msg(sock_id, target, in_nick + ", ai primit " + str(linguri[in_nick])
                + " linguri de lemn pana acum, ouch!")
    else:
        Xfs.Msg(sock_id, target, in_nick + ", felicitari! Esti unul dintre cei norocosi"
                + " care nu a primit nici o lingura de lemn... inca.")

def ShowTopLingura(Xfs, sock_id, target):
    """Sort and display top10."""
    with open(l_path, 'r') as f:
        linguri = json.load(f)

    loc = 1
    Xfs.Msg(sock_id, target, "Top10 linguri de lemn primite:")
    for nick, primite in sorted(linguri.items(), reverse=True, key=lambda item: (item[1], item[0])):
        if (loc <= 10 and nick != 'info_linguri'):
            Xfs.Msg(sock_id, target, str(loc) + ". " + "%s %s" % (nick, primite))
            loc +=1

    Xfs.Msg(sock_id, target, "Total linguri de lemn primite: " + str(linguri['info_linguri']))


def GetLingura(func):
    def wrapper_func(Xfs, sock_id, Raw):
        func(Xfs, sock_id, Raw)
        split_line = Raw.line.split(" ")
        if (Raw.raw_type == "PRIVMSG" and Raw.line[0] == "\001"
            and Raw.line[-1] == "\001" and Raw.target == "#filelist" and Raw.in_nick == "rose"
            and "lingura" in Raw.line and "lemn" in Raw.line and len(split_line) == 9):
            lingura_nick = split_line[8][:-1]
            AddLingura(Xfs, sock_id, Raw.target, lingura_nick)
    return wrapper_func


def TriggerLingura(func):
    """Add triggers to module."""
    def wrapper_func(Xfs, sock_id, Raw):
        func(Xfs, sock_id, Raw)
        if (Raw.target == "#filelist" and Raw.cmd == ".lingura" and Raw.line == Raw.cmd):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            """Only owner and rose can show top10."""
            if (Raw.in_nick != Xfs.owner and Raw.in_nick != "rose"):
                ShowLingura(Xfs, sock_id, Raw.target, Raw.in_nick)
            if (Raw.in_nick == Xfs.owner or Raw.in_nick == "rose"):
                ShowTopLingura(Xfs, sock_id, Raw.target)
    return wrapper_func
        
    
        

    
    
    
