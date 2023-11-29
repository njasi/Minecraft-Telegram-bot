# Minecraft-Telegram-bot

## About

Basic server telegram bot that can interface with minecraft servers in a couple of ways:

- ping public facing servers and get info
- control local whitelist.json files
- control local minecraft server

There are some visuals built into the bot

## Interface

There are some nice visuals the bot renders for you:

- The `/status` command mimics the minecraft launcher, rendered using the `html2image` package:
  ![hypixel example image](public/hypixel.jpg)
- The `/whitelistadd` command renders the user's skin with [NickAc's Minecraft Skin Renderer](https://nmsr.nickac.dev/) so you can be sure you've added the right person:
  <img src="public/whitelist.png" data-canonical-src="public/whitelist.png" width="200"/>
- The `/online` command is planned to render the users like a tablist, likely using the `htm2image` package


## Installation

I would reccomend using this in a venv since there are some cluttersome packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -R requirements.txt
```

## Setup

This bot is not a plugin or mod like some are, but this does make it usable for any server type. I have developed it for linux though, what kind of monster would use a windows server for minecraft.

Might rewrite it for usability on windows though.

If you want the bot to be able to control your minecraft server, you should run it locally on your server. Using tmux to manage the session gives you extra control.

### Hosts json file

An array of your saved hosts.

```json
[
  {
    "name": "My Minecraft Server",
    "hostname": "my.minecraft.server.com",
    "port": 25565,
    "local": true,
    "whitelist_path": "/srv/minecraft/whitelist.json",
    "systemctl_name": "minecraft",
    "tmux_name": "minecraft",
  },
  {
    "name": "Hypixel",
    "hostname": "mc.hypixel.net",
    "port": 25565,
    "local": false,
    "whitelist_path": "",
    "systemctl_name": "",
    "tmux_name": ""
  },
];
```

Values:

- `name`: The pretty name visible by default to commands like /status.
- `hostname`: The ip address of the server (can use localhost, but it wont display the external facing ip when you ask for it)
- `port`: The port the server is running on, will be displayed if is non default when prompted for the hostname.
- `local`: True if this server is local
- `whitelist_path`: Path to the whitelist.json file for this local server
- `systemctl_name`: Service name of the server
- `tmux_name`: Name of the tmux session your server runs in.

### .env

```bash
# telegram bot config
DEVELOPER_CHAT_ID = "DEV_CHAT_ID"
TOKEN             = "TELEGRAM_BOT_TOKEN"
WHITELIST_PATH    = "./tmp.json"

# default minecraft server config
SERVER_HOST = "host.name"
SERVER_PORT = 25565
```

Values:

- `DEVELOPER_CHAT_ID`: chat id where you want errors sent
- `TOKEN`: telegram bot token
- `SERVER_HOST`: hostname of the default server
- `SERVER_PORT`: port of the default server

### Other

This project uses the `html2image` package, which uses a browser in headless mode to render html. This means you need a browser like chrome installed on the server computer.

## Commands

- `/online hostname`:
  TODO
  Check what players are online (obsfucated by some servers)
- `/status [hostname...] -a,--all -h,--hostname`
  Check server(s) status, renders motd like in the minecraft launcher.
  - `-a`, `--all`: show all of the hosts in your hosts file.
  - `-h`, `--hostname`: show hostnames instead of pretty names.
    d
- `/ping hostname`:
  Measure the response time of the server.

### Admin commands

- `/serverstop`:
  TODO
  Stop the server
- `/serverstart`:
  TODO
  Start the server
- `/serverrestart`:
  TODO
  Restart the server
- `/whitelistadd username`:
  Add player to the whitelist
- `/whitelistrm username`:
  Remove player from the whitelist
- `/activate hostname`:
  Set active server for general commands

### General admin commands:

Any command that is not reconized will be sent directly to the active server console via tmux
