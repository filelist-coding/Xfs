# Grabs the bot settings from cfg/config.ini

import configparser

config = configparser.ConfigParser()
config.read("cfg\\config.ini")

# settings

server = config['network']['server']
port = int(config['network']['port'])
nick = config['user']['nick']
alt_nick = config['user']['alt_nick']
nick_pass = config['user']['nick_pass']
invite_key = config['user']['invite_key']
ident = config['user']['ident']
real_name = config['user']['real_name']
ctcp_version_reply = config['ctcp']['version']
owner = config['owner']['nick']
channels = config['autojoin']['channels']
owner_host = config['owner']['host']