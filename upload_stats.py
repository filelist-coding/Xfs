import re
import json
import time
import cmd_logger


def MBToGB(mb):
    """Convert MB to GB."""
    return mb/1000

def KBToGB(kb):
    """Convert kB to GB."""
    return kb/1000000


def AddStat(line):
    s_path = "db\\" + time.strftime('%Y.%m.%d.upstats.json')

    try:
        file = open(s_path, 'r')
        up_stats = json.load(file)
        file.close()
        p_type = re.compile("\00306\[(.+)\]\s")
        p_size = re.compile("\00306\[.+\]\s\[(.+)\s..\]\003")
        p_size_type = re.compile("\00306\[.+\]\s\[.+\s(..)\]\003")
        
        s_type = p_type.search(line)
        s_size = p_size.search(line)
        s_size_type = p_size_type.search(line)
        r_type = s_type.group(1)
        r_size = float(s_size.group(1))
        r_size_type = s_size_type.group(1)
        if (r_size_type == "MB"):
            r_size = float(MBToGB(r_size))
        elif (r_size_type == "kB"):
            r_size = float(KBToGB(r_size))

        if (r_type in up_stats):
            up_stats[r_type] += float(r_size)
        else:
            up_stats[r_type] = float(r_size)
        """Add values to total_size and freeleech."""
        up_stats['total_size'] += float(r_size)
        up_stats['freeleech'] += float(r_size) if "[\00304FreeLeech!\003]" in line else 0

        file = open(s_path, 'w')
        json.dump(up_stats, file)
        file.close()
        
        
    except:
        """There is no file with stats for this day."""
        file = open(s_path, 'w')
        up_stats = {}

        p_type = re.compile("\00306\[(.+)\]\s")
        p_size = re.compile("\00306\[.+\]\s\[(.+)\s..\]\003")
        p_size_type = re.compile("\00306\[.+\]\s\[.+\s(..)\]\003")
        
        s_type = p_type.search(line)
        s_size = p_size.search(line)
        s_size_type = p_size_type.search(line)
        r_type = s_type.group(1)
        r_size = float(s_size.group(1))
        r_size_type = s_size_type.group(1)
        if (r_size_type == "MB"):
            r_size = float(MBToGB(r_size))
        elif (r_size_type == "kB"):
            r_size = float(KBToGB(r_size))
        up_stats['total_size'] = float(r_size)
        up_stats['freeleech'] = float(r_size) if "[\00304FreeLeech!\003]" in line else 0
        up_stats[r_type] = float(r_size)
        json.dump(up_stats, file)
        file.close()
        

def ShowStats(Xfs, sock_id, target):
    s_path = "db\\" + time.strftime('%Y.%m.%d.upstats.json')

    try:
        file = open(s_path, 'r')
        up_stats = json.load(file)
        file.close()
        upload = up_stats['total_size']
        freeleech = 0
        filme = 0
        seriale = 0
        jocuri = 0
        audio = 0
        altele = 0

        for k in up_stats:
            if (k == 'freeleech'):
                freeleech += up_stats[k]
            elif ("Filme" in k):
                filme += up_stats[k]
            elif ("Seriale" in k):
                seriale += up_stats[k]
            elif ("Jocuri" in k):
                jocuri += up_stats[k]
            elif ("Audio" in k):
                audio += up_stats[k]
            else:
                if ("total_size" not in k):
                    altele += up_stats[k]

        stat_line = ("[" + time.strftime('%d.%m.%Y') + " stats] Upload:\00304 " + '{:.2f}'.format(float(upload)) + "GB\003 | FreeLeech:\0033 "
                     + '{:.2f}'.format(float(freeleech)) + "GB\003 | Filme:\00312 " + '{:.2f}'.format(float(filme)) + "GB\003 | Seriale:\00312 "
                     + '{:.2f}'.format(float(seriale)) + "GB\003 | Jocuri:\00312 " + '{:.2f}'.format(float(jocuri)) + "GB\003 | Audio:\00312 "
                     + '{:.2f}'.format(float(audio)) + "GB\003 | Altele:\00312 " + '{:.2f}'.format(float(altele)) + "GB\003")
        

        Xfs.Msg(sock_id, target, stat_line)
    except:
        Xfs.Msg(sock_id, target, "Nu au fost inregistrate statistici de upload pentru " + time.strftime('%d.%m.%Y'))

        
def GetStat(func):
    def wrapper_func(Xfs, sock_id, Raw):
        func(Xfs, sock_id, Raw)
        if (Raw.raw_type == "PRIVMSG" and Raw.target == "#announce" and Raw.in_nick == "Announce"
            and "by" in Raw.line):
            AddStat(Raw.line)
    return wrapper_func

def TriggerStat(func):
    def wrapper_func(Xfs, sock_id, Raw):
        func(Xfs, sock_id, Raw)
        if (Raw.in_nick == Xfs.owner and Raw.in_host == Xfs.owner_host
            and Raw.cmd == ".uploadstats" and Raw.line == Raw.cmd):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            ShowStats(Xfs, sock_id, Raw.target)
    return wrapper_func

