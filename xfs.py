# Main class for the Bot

import socket
import time
import re
import config_bot
import xfs_handler


class Xfs:
    def __init__(self):
        """Loads all the bot settings."""
        self.server = config_bot.server
        self.port = config_bot.port
        self.nick = config_bot.nick
        self.alt_nick = config_bot.alt_nick
        self.nick_pass = config_bot.nick_pass
        self.invite_key = config_bot.invite_key
        self.ident = config_bot.ident
        self.real_name = config_bot.real_name
        self.ctcp_version_reply = config_bot.ctcp_version_reply
        self.owner = config_bot.owner
        self.owner_host = config_bot.owner_host
        self.channels = config_bot.channels
          
    def Send(self, sock_id, raw):
        """Appends \r\n to end of raw and sends to socket."""
        print(time.strftime("[%H:%M:%S]") + " OUT: " + raw)
        raw = raw + "\r\n"
        sock_id.send(bytes(raw, "UTF-8"))
        
    def Recv(self, sock_id):
        """Retrieves raws from socket."""
        self.recv_buffer = sock_id.recv(2048).decode("UTF-8")
        xfs_handler.RawParser(self, sock_id, self.recv_buffer)

    def Pong(self, sock_id, reply):
        """Sends reply to PING raw from socket."""
        raw = "PONG " + reply
        self.Send(sock_id, raw)

    def Nick(self, sock_id, nick):
        """Sends NICK raw to socket."""
        raw = "NICK " + nick
        self.Send(sock_id, raw)

    def AltNick(self, sock_id):
        """Sends NICK raw to socket with alt_nick."""
        self.Nick(sock_id, self.alt_nick)
 
    def User(self, sock_id):
        """Sends USER raw to socket."""
        raw = ("USER " + self.ident + " " + self.nick + " " + self.nick + " " + self.real_name)
        self.Send(sock_id, raw)

    def Msg(self, sock_id, target, msg):
        """Sends PRIVMSG raw to socket."""
        raw = "PRIVMSG " + target + " :" + msg
        self.Send(sock_id, raw)

    def Notice(self, sock_id, target, msg):
        """Sends NOTICE raw to socket."""
        raw = "NOTICE " + target + " :" + msg
        self.Send(sock_id, raw)

    def Join(self, sock_id, target, key = ""):
        """Sends JOIN raw to socket."""
        if (len(key) == 0):
            raw = "JOIN " + target
            self.Send(sock_id, raw)
        else:
            raw = "JOIN " + target + " " + key
            self.Send(sock_id, raw)

    def Part(self, sock_id, target, msg = "Leaving channel!"):
        """Sends PART raw to socket."""
        raw = "PART " + target + " " + msg
        self.Send(sock_id, raw)

    def Kick(self, sock_id, target, chan, msg = "Out!"):
        """Sends KICK raw to socket."""
        raw = "KICK {} {} :{}".format(chan, target, msg)
        self.Send(sock_id, raw)

    def Quit(self, sock_id, msg = "Leaving server!"):
        """Sends QUIT raw to socket."""
        raw = "QUIT " + msg
        self.Send(sock_id, raw)

    def Identify(self, sock_id):
        """Authentificates nick to NickServ."""
        self.Msg(sock_id, "NickServ", "identify " + self.nick_pass)
        
    def RecoverNick(self, sock_id):
        """Recovers nick from NickServ."""
        raw = "recover " + self.nick + " " + self.nick_pass
        self.Msg(sock_id, "NickServ", raw)

    def RestartBot(self, sock_id):
        """Restarts socket connection."""
        self.Quit(sock_id)
        self.Run()

    def CTCPVersionReply(self, sock_id, target):
        """Sends CTCP reply to VERSION."""
        raw = chr(1) + "VERSION " + self.ctcp_version_reply + chr(1)
        self.Notice(sock_id, target, raw)

    def AutoJoin(self, sock_id):
        """Joins channels listed in cfg/config.ini."""
        p_chan_key = re.compile("\:(.+)$")
        p_chan = re.compile("^(.+)\:")
        channel_list = self.channels.split(",")

        for chan in channel_list:
            if (":" in chan):
                """Check if there is a key."""
                r_chan_key = p_chan_key.search(chan)
                r_chan = p_chan.search(chan)
                chan_key = r_chan_key.group(1)
                channel = r_chan.group(1)
                self.Join(sock_id, channel, chan_key)
            else:
                self.Join(sock_id, chan)
         
    def Run(self):
        """Starts all the socket/dns stuff."""
        try:
            self.irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.irc_sock.connect((self.server, self.port))
            self.User(self.irc_sock)
            self.Nick(self.irc_sock, self.nick)
        except TimeoutError:
            print("Could not connect to address, trying again...")
            self.Run()
  
        
        # TODO: Improve Exception Handling
        while True:
            try:
                self.Recv(self.irc_sock)
            except:
                print("Unexpected error!")
                raise

    # TODO: Finish all the default functions

def BotStart():
    xfs_bot = Xfs()
    xfs_bot.Run()

"""Start the BOT."""
BotStart()
