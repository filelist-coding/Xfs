# IMDB module
# Grabs info from imdb.com using omdbapi.com API

import json
import requests
import cmd_logger
import threading
import re


def GetIMDB(Xfs, sock_id, in_nick, target, title, year = "", request_type = "t"):
    """ Get info about movie and tv-series from API."""

    url = ""
    """Send API request by title or id."""
    if (request_type == "t"):
        url = ("http://www.omdbapi.com/?apikey=API-KEY&t=" + title + "&y=" + year)
    elif (request_type == "i"):
        url = ("http://www.omdbapi.com/?apikey=API-KEY&i=" + title + "&y=" + year)
        
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)

    if (response.status_code == 200):
        imdb_info = json.loads(response.content.decode("utf-8"))
        if (imdb_info["Response"] == "True"):
            mv_title = imdb_info["Title"]
            mv_release = imdb_info["Released"]
            mv_runtime = imdb_info["Runtime"]
            mv_genre = imdb_info["Genre"]
            mv_plot = imdb_info["Plot"]
            mv_imdb_r = imdb_info["imdbRating"]
            mv_imdb_l = "http://www.imdb.com/title/" + imdb_info["imdbID"] + "/"
            raw = ("\00303" + mv_title + "\003: " + mv_plot + " |\00304 " + mv_imdb_r + "\003 IMDB | " + mv_release
                   + " | " + mv_runtime + " | " + mv_genre + " | " + mv_imdb_l)
            Xfs.Msg(sock_id, target, raw)
        else:
            raw = "Eroare! Nu s-a gasit nici un rezultat, asigurate ca ai numele si/sau anul corect."
            Xfs.Notice(sock_id, in_nick, raw)
    else:
        print("Error! non-200 response from API.")



def TriggerGetIMDB(func):
    """Wrapper for .imdb trigger."""
    def wrapper_func(Xfs, sock_id, Raw):
        func(Xfs, sock_id, Raw)
        line_split = Raw.line.split(" ")
        if (Raw.cmd == ".imdb"):
            cmd_logger.AddLog(Raw.in_nick, Raw.target, Raw.cmd)
            if (Raw.cmd == Raw.line):
                Xfs.Notice(sock_id, Raw.in_nick, "Erroare! Sintaxa corecta este: .imdb <titlu> <an=N>* | "
                           + "Exemplu 1: .imdb Pulp Fiction | Exemplu 2: .imdb Star Wars an=2017")
            else:
                p_is_year = re.compile(".*\san\=\d\d\d\d$")
                p_year = re.compile(".*\san\=(\d\d\d\d)$")
                if (p_is_year.match(Raw.line) is not None):
                    year_r = p_year.search(Raw.line)
                    year = year_r.group(1)
                    p_title = re.compile("^\.imdb\s(.*)\san\=\d\d\d\d$")
                    title_r = p_title.search(Raw.line)
                    title = title_r.group(1)
                    imdb_thread = threading.Thread(target=GetIMDB,
                                                   args=(Xfs, sock_id, Raw.in_nick, Raw.target, title, year),
                                                   kwargs={"request_type": "t"})
                    imdb_thread.start()
                else:
                    imdb_thread = threading.Thread(target=GetIMDB,
                                                   args=(Xfs, sock_id, Raw.in_nick, Raw.target, Raw.line[6:]),
                                                   kwargs={"request_type": "t"})
                    imdb_thread.start()
    return wrapper_func


def GrabIMDBLink(func):
    """Wrapper for triggering GetIMDB() from link pasted in a channel."""
    def wrapper_func(Xfs, sock_id, Raw):
        func(Xfs, sock_id, Raw)
        p_is_imdb = re.compile(".*www\.imdb\.com\/title\/tt\d+\/.*")
        p_grab_id = re.compile(".*www\.imdb\.com\/title\/(tt\d+)\/.*")
        if (Raw.raw_type == "PRIVMSG" and Raw.in_nick != "Xfs" and Raw.line[0] != "\001"):
            if (p_is_imdb.match(Raw.line) is not None):
                grab_id_r = p_grab_id.search(Raw.line)
                movie_id = grab_id_r.group(1)
                imdb_thread = threading.Thread(target=GetIMDB,
                                               args=(Xfs, sock_id, Raw.in_nick, Raw.target, movie_id),
                                               kwargs={"request_type": "i"})
                imdb_thread.start()
    return wrapper_func
