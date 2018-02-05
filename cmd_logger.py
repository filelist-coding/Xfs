# Log command and other stuff usage from bot

import time

def AddLog(nick, target, cmd):
    """Add log entry."""
    log_name = time.strftime('%Y.%m.%d.log.txt')
    log_time = time.strftime('[%H:%M:%S]')
    log_entry = log_time + " " + nick + ", used: " + cmd + " in " + target + "\n"

    with open("logs\\" + log_name, 'a') as f:
        f.write(log_entry)
