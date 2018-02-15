# Parses and handles all the raws from socket

import time
import re
import misc_func
import cmd_logger
import crypto
import lingura
import upload_stats
import btc_addr
import imdb

class Raw:
    """Raw object that holds all the parsed data from socket."""
    def __init__(self, raw_type, in_host = "", in_nick = "", target= ""
                 , mode = "", line = "", is_cmd = False, cmd = ""):
        self.raw_type = raw_type
        self.in_host = in_host
        self.in_nick = in_nick
        self.target = target
        self.mode = mode
        self.line =line
        self.is_cmd = is_cmd
        self.cmd = cmd
    

def RawParser(Xfs, sock_id, raw):
    """Removes \n and \r from raws and parses them into lines for RawHandler()."""
    line = ""
    for char in raw:
        if (char != "\r" and char != "\n"):
            line += char
        else:
            if (len(line) != 0):
                RawHandler(Xfs, sock_id, line)
                line = ""

def RawHandler(Xfs, sock_id, raw):
    """Parses the raws from socket into alpha and numerical raw objects and sends them to
    their respective handlers.
    """

    
    """Prints the incoming raw from socket, format: [15:23:10] IN: raw."""   
    print(time.strftime("[%H:%M:%S]") + " IN: " + raw)
    split_raw = raw.split(" ")
    """Holds the type of the raw, ex: 433 or PRIVMSG."""
    raw_type = split_raw[1]

    if (split_raw[0] == "PING"):
        Xfs.Pong(sock_id, split_raw[1])
    elif (misc_func.IsAlpha(raw_type) == True):
        """RAW is alpha."""
        if (split_raw[0] != ":" + Xfs.server):
            if (raw_type == "PRIVMSG" or raw_type == "NOTICE"):
                """p_in_nick matches John from :John!test@qq.com."""
                p_in_nick = re.compile("^\:(.+)\!")
                r_in_nick = p_in_nick.search(split_raw[0])
                in_nick = r_in_nick.group(1)
                """p_in_host matches qq.com from :John!test@qq.com."""
                p_in_host = re.compile("\@(.+)$")
                r_in_host = p_in_host.search(split_raw[0])
                in_host = r_in_host.group(1)
                target = split_raw[2]
                """p_line matchs everything after the second ':' inside the raw, i.e. the msg"""
                p_line = re.compile("\s\:(.+)$")
                r_line = p_line.search(raw)
                line = r_line.group(1)
                is_cmd = False
                cmd = ""
                if (line[0] == "." and len(line) > 1):
                    is_cmd = True
                    split_line = line.split(" ")
                    cmd = split_line[0]
                raw_obj = Raw(raw_type = raw_type, in_host = in_host, in_nick = in_nick, target = target
                              , line = line, is_cmd = is_cmd, cmd = cmd)
                AlphaRawHandler(Xfs, sock_id, raw_obj)
                
            elif (raw_type == "INVITE"):
                """p_in_nick matches John from :John!test@qq.com."""
                p_in_nick = re.compile("^\:(.+)\!")
                r_in_nick = p_in_nick.search(split_raw[0])
                in_nick = r_in_nick.group(1)
                """p_in_host matches qq.com from :John!test@qq.com."""
                p_in_host = re.compile("\@(.+)$")
                r_in_host = p_in_host.search(split_raw[0])
                in_host = r_in_host.group(1)
                invite_chan = split_raw[3][1:]
                if (in_nick == "System" and invite_chan == "#filelist"):
                    Xfs.Join(sock_id, invite_chan)
            
    elif (misc_func.IsNum(raw_type) == True):
        """RAW is numerical."""
        if (split_raw[0] == ":" + Xfs.server):
            raw_obj = Raw(raw_type = raw_type)
            NumRawHandler(Xfs, sock_id, raw_obj)


@upload_stats.GetStat
@lingura.GetLingura
@imdb.GrabIMDBLink
def AlphaRawHandler(Xfs, sock_id, Raw):
    """Interprets and handles alpha raws from socket."""
    split_line = Raw.line.split(" ")
    if (Raw.raw_type == "PRIVMSG"):
        """PRIVMSG section."""
        if (Raw.is_cmd == True):
            CmdHandler(Xfs, sock_id, Raw)
        elif (Raw.target == Xfs.nick):
            if (Raw.line == "help"):
                cmd_logger.AddLog(Raw.in_nick, Raw.target, "help")
                help_msg = ("Comenzi disponibile pe canal: .lingura | .crypto | .btcaddr <address> | .imdb <titlu> <an=N>*")
                Xfs.Msg(sock_id, Raw.in_nick, help_msg)
            if (Raw.line == "\001VERSION\001"):
                """Version CTCP."""
                Xfs.CTCPVersionReply(sock_id, Raw.in_nick)
                
        elif (Raw.line[0] == "\001" and Raw.line[-1] == "\001"):
            """ACTION section."""
                
    elif (Raw.raw_type == "NOTICE"):
        """NOTICE section."""
        if (Raw.in_nick == "NickServ"):
            if ("registered" in Raw.line and "protected" in Raw.line):
                """Auth to NickServ."""
                Xfs.Identify(sock_id)
            elif ("password" in Raw.line and "email" in Raw.line):
                """Bot is using alt_nick, recover main nick."""
                Xfs.RecoverNick(sock_id)
            elif ("now" in Raw.line and "identified!" in Raw.line):
                """Run stuff when identified."""
                Xfs.AutoJoin(sock_id)
                Xfs.Msg(sock_id, "System", "invite " + str(Xfs.invite_key))
            

def NumRawHandler(Xfs, sock_id, Raw):
    """Interprets and handles numerical raws from socket."""
    if (Raw.raw_type == "433"):
        """Nick already used, recover it."""
        Xfs.AltNick(sock_id)
    

@crypto.TriggerCrypto
@lingura.TriggerLingura
@upload_stats.TriggerStat
@btc_addr.TriggerGetAddr
@imdb.TriggerGetIMDB
def CmdHandler(Xfs, sock_id, Raw):
    """Executes commands."""
    split_line = Raw.line.split(" ")
    split_line_size = len(split_line)
    if (Raw.in_nick == Xfs.owner and Raw.in_host == Xfs.owner_host):
        if (Raw.cmd == ".join"):
            """Join command."""
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            if (split_line_size == 1):
                Xfs.Msg(sock_id, Raw.target, "ERROR. Syntax is: .join <#chan> <key>*")
            elif (split_line_size == 2):
                if (split_line[1][0] != "#"):
                    Xfs.Msg(sock_id, Raw.target, "ERROR. Syntax is: .join <#chan> <key>*")
                else:
                    Xfs.Join(sock_id, split_line[1])
            elif (split_line_size == 3):
                if (split_line[1][0] != "#"):
                    Xfs.Msg(sock_id, Raw.target, "ERROR. Syntax is: .join <#chan> <key>*")
                else:
                    Xfs.Join(sock_id, split_line[1], split_line[2])
        elif (Raw.cmd == ".part"):
            """Part command."""
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            if (split_line_size == 1):
                Xfs.Part(sock_id, Raw.target)
            elif (split_line_size == 2):
                if (split_line[1][0] != "#"):
                    Xfs.Msg(sock_id, Raw.target, "ERROR. Syntax is: .part <#chan>*")
                else:
                    Xfs.Part(sock_id, split_line[1])
        elif (Raw.cmd == ".quit"):
            """Quit command."""
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            if (split_line_size == 1):
                Xfs.Quit(sock_id)
            else:
                Xfs.Quit(sock_id, "".join(split_line[1:]))
        elif (Raw.cmd == ".restart"):
            """Restart command."""
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            if (split_line_size == 1):
                Xfs.RestartBot(sock_id)
        elif (Raw.cmd == ".kick"):
            """Kick command."""
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            if (split_line_size == 1):
                Xfs.Notice(sock_id, Raw.in_nick, "Error. Syntax is .kick <nick> <reason>*")
            elif (split_line_size == 2):
                Xfs.Kick(sock_id, split_line[1], Raw.target)
            elif (split_line_size >= 3):
                Xfs.Kick(sock_id, split_line[1], Raw.target, " ".join(split_line[2:]))
        elif (Raw.cmd == ".sendraw"):
            """Sends raw to server."""
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            if (split_line_size != 1):
                Xfs.Send(sock_id, " ".join(split_line[1:]))