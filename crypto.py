# Crypto stuff

import json
import requests
import cmd_logger
import threading

def GetCrypto(Xfs, sock_id, in_nick, target, coin):
    """Get information about coin from API."""
    with open("db\crypto_symbols.json", 'r') as f:
        symbols = json.load(f)
    if (coin.upper() in symbols):
        """Check if coin can be found in the symbol json."""
        coin_symbol = symbols[coin.upper()]
        url = "https://api.coinmarketcap.com/v1/ticker/" + coin_symbol + "/?convert=EUR"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        if (response.status_code == 200):
            crypto_info = json.loads(response.content.decode("utf-8"))[0]
            name = crypto_info['name']
            symbol = crypto_info['symbol']
            p_usd = ''
            p_eur = ''
            tmp_p_usd = float(crypto_info['price_usd'])
            tmp_p_eur = float(crypto_info['price_eur'])
            """Format the fiat value of the coin to the relevant decimal point."""
            if (tmp_p_usd >= 0.01):
                p_usd = '{:,.2f}'.format(tmp_p_usd)
            elif (tmp_p_usd >= 0.001 and tmp_p_usd < 0.01):
                p_usd = '{:,.3f}'.format(tmp_p_usd)
            elif (tmp_p_usd >= 0.0001 and tmp_p_usd < 0.001):
                p_usd = '{:,.4f}'.format(tmp_p_usd)
            if (tmp_p_eur >= 0.01):
                p_eur = '{:,.2f}'.format(tmp_p_eur)
            elif (tmp_p_eur >= 0.001 and tmp_p_eur < 0.01):
                p_eur = '{:,.3f}'.format(tmp_p_eur)
            elif (tmp_p_eur >= 0.0001 and tmp_p_eur < 0.001):
                p_eur = '{:,.4f}'.format(tmp_p_eur)

            p_btc = crypto_info['price_btc']
            rank = crypto_info['rank']
            c_1h = float(crypto_info['percent_change_1h'])
            c_24h = float(crypto_info['percent_change_24h'])
            c_7d = float(crypto_info['percent_change_7d'])
            """Format the colour of the 7d/24h/1h data depending if it's positive or not.
            Red is for negative, green is for positive.
            """
            if (c_1h >= 0):
                c_1h = "\003" + "3+" + str(c_1h) + "%" + "\003"
            elif (c_1h < 0):
                c_1h = "\003" + "4" + str(c_1h) + "%" + "\003"
            if (c_24h >= 0):
                c_24h = "\003" + "3+" + str(c_24h) + "%" + "\003"
            elif (c_24h < 0):
                c_24h = "\003" + "4" + str(c_24h) + "%" + "\003"
            if (c_7d >= 0):
                c_7d = "\003" + "3+" + str(c_7d) + "%" + "\003"
            elif (c_7d < 0):
                c_7d = "\003" + "4" + str(c_7d) + "%" + "\003"
            """Customize symbols colours."""
            if (symbol == "BTC"):
                symbol = "\003" + "0,7(" + symbol + ")" + "\003"
            elif (symbol == "LTC"):
                symbol = "\003" + "0,14(" + symbol + ")" + "\003"
            elif (symbol == "ETH"):
                symbol = "\003" + "0,1(" + symbol + ")" + "\003"
            elif (symbol == "XRP"):
                symbol = "\003" + "0,12(" + symbol + ")" + "\003"
            elif (symbol == "BCH"):
                symbol = "\003" + "0,7(" + symbol + ")" + "\003"
            elif (symbol == "DASH"):
                symbol = "\003" + "0,12(" + symbol + ")" + "\003"
            elif (symbol == "XMR"):
                symbol = "\003" + "7,1(" + symbol + ")" + "\003"
            elif (symbol == "OMG"):
                symbol = "\003" + "0,12(" + symbol + ")" + "\003"
            elif (symbol == "ZEC"):
                symbol = "\003" + "8,1(" + symbol + ")" + "\003"
            elif (symbol == "XVG"):
                symbol = "\003" + "12,11(" + symbol + ")" + "\003"
            elif (symbol == "TRX"):
                symbol = "\003" + "0,1(" + symbol + ")" + "\003"
            elif (symbol == "AEON"):
                symbol = "\003" + "11,12(" + symbol + ")" + "\003"
            elif (symbol == "XLR"):
                symbol = "\003" + "1,8(" + symbol + ")" + "\003"
            elif (symbol == "ETC"):
                symbol = "\003" + "3,15(" + symbol + ")" + "\003"
            elif (symbol == "GNT"):
                symbol = "\003" + "1,15(" + symbol + ")" + "\003"
            else:
                symbol = "(" + symbol + ")"

            """Construct raw and send."""
            raw = (name + " " + symbol + ":" + "\003" + "3 " + p_usd + "$" + "\003" + " -" + "\003" + "12 "
                   + p_eur + chr(8364) + "\003" + " | " + p_btc + " BTC | Loc: " + rank + " | (7d) " + c_7d
                   + " | (24h) " + c_24h + " | (1h) " + c_1h)
            Xfs.Msg(sock_id, target, raw)
        else:
            print("ERROR: API response is non-200")
    else:
        raw = ("Eroare! Moneda introdusa nu a fost gasita in baza de date.")
        Xfs.Notice(sock_id, in_nick, raw)


def TriggerCrypto(func):
    """Add triggers to module."""
    def wrapper_func(Xfs, sock_id, Raw):
        func(Xfs, sock_id, Raw)
        line_split = Raw.line.split(" ")
        if (Raw.cmd == ".cmc" and len(line_split) == 2):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd + " " + line_split[1])
            crypto_thread = threading.Thread(target = GetCrypto, args = (Xfs, sock_id, Raw.in_nick, Raw.target, line_split[1]))
            crypto_thread.start()
        elif (Raw.cmd == ".cmc" and Raw.cmd == Raw.line):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            Xfs.Notice(sock_id, Raw.in_nick, "Eroare! Sintaxa corecta este: .cmc <moneda> | Exemplu: .cmc xrp")
        elif (Raw.cmd == ".btc" and Raw.cmd == Raw.line):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            crypto_thread = threading.Thread(target = GetCrypto, args = (Xfs, sock_id, Raw.in_nick, Raw.target, "btc"))
            crypto_thread.start()
        elif (Raw.cmd == ".bch" and Raw.cmd == Raw.line):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            crypto_thread = threading.Thread(target = GetCrypto, args = (Xfs, sock_id, Raw.in_nick, Raw.target, "bch"))
            crypto_thread.start()
        elif (Raw.cmd == ".eth" and Raw.cmd == Raw.line):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            crypto_thread = threading.Thread(target = GetCrypto, args = (Xfs, sock_id, Raw.in_nick, Raw.target, "eth"))
            crypto_thread.start()
        elif (Raw.cmd == ".xmr" and Raw.cmd == Raw.line):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            crypto_thread = threading.Thread(target = GetCrypto, args = (Xfs, sock_id, Raw.in_nick, Raw.target, "xmr"))
            crypto_thread.start()
        elif (Raw.cmd == ".ltc" and Raw.cmd == Raw.line):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            crypto_thread = threading.Thread(target = GetCrypto, args = (Xfs, sock_id, Raw.in_nick, Raw.target, "ltc"))
            crypto_thread.start()
        elif (Raw.cmd == ".crypto" and Raw.cmd == Raw.line):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            Xfs.Msg(sock_id, Raw.target, "Comenzi disponibile pentru crypto-currency: "
                    + ".btc | .bch | .eth | .xmr | .ltc | Pt. alte monede folositi: .cmc <moneda> |"
                    + " Exemplu: .cmc xrp")
    return wrapper_func

