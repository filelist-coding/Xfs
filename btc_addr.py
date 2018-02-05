# Calls API from blockchain.info to get info about BTC address

import json
import requests
import cmd_logger
import threading


def SatoshiToBTC(nr):
    """Converts satoshi to BTC."""
    return nr/100000000


def GetAddr(Xfs, sock_id, target, btc_addr):
    """ Grab info from API."""
    url = "https://blockchain.info/rawaddr/" + btc_addr + "?offset=100&?format=json"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)

    if (response.status_code == 200):
        addr_info = json.loads(response.content.decode("utf-8"))
        extra_info = "https://blockchain.info/address/"

        raw = ("Transactions:\00312 " + str(addr_info['n_tx']) + "\003 | Balance:\00312 " + str(SatoshiToBTC(addr_info['final_balance']))
               + "\003 BTC | Total Sent:\0034 " + str(SatoshiToBTC(addr_info['total_sent'])) + "\003 BTC | Total Received:\0033 "
               + str(SatoshiToBTC(addr_info['total_received'])) + "\003 BTC | More: " + extra_info + btc_addr)
        Xfs.Msg(sock_id, target, raw)


    else:
        print("ERROR: non-200 response from API")


def TriggerGetAddr(func):
    """Add trigers to module."""
    def wrapper_func(Xfs, sock_id, Raw):
        func(Xfs, sock_id, Raw)
        if (Raw.cmd == ".btcaddr"):
            split_line = Raw.line.split(" ")
            if (len(split_line) == 2 and len(split_line[1]) == 34 and split_line[1].isalnum() == True):
                cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
                addr_thread = threading.Thread(target=GetAddr, args=(Xfs, sock_id, Raw.target, split_line[1]))
                addr_thread.start()
    return wrapper_func
                
