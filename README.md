# Minecraft-Telegram-bot

## About

This is a basic server telegram bot that can interface with minecraft servers in a couple of ways:

- ping public facing servers and get info
- control local minecraft server
- control local whitelist.json files
- TODO control local blacklist.json files?
- TODO control server.properties settings?

This bot is not a plugin or a mod, it is a standalone python program. If setup local to your minecraft servers it'll have access to their consoles through a FIFO file (see setup instructions and details below). This also means that it could be used for basically any version of minecraft. I plan to use it to manage 3 servers of differing versions at once.

## Interface overview

There are some nice visuals the bot provides:

- The `/status` command mimics the minecraft launcher, rendered using the `html2image` package:
  ![hypixel example image](public/hypixel.jpg)
- The `/whitelistadd` command renders the user's skin with [NickAc's Minecraft Skin Renderer](https://nmsr.nickac.dev/) so you can be sure you've added the right person:
  <img src="public/whitelist.png" data-canonical-src="public/whitelist.png" width="200"/>
- The `/online` command is planned to render the users like a tablist, likely using the `htm2image` package

## Setup

### Python enviroment

I would reccomend using this in a venv since there are some cluttersome packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -R requirements.txt
```

### Hosts json file

An array of your saved hosts.

```json
[
  {
    "name": "My Minecraft Vanilla Server",
    "hostname": "my.minecraft.server.com",
    "port": 25565,
    "local": true,
    "whitelist_path": "/srv/minecraft/vanilla/whitelist.json",
    "systemctl_name": "minecraft",
    "systemctl_ext": "vanilla",
    "default": true
  },
  {
    "name": "My Minecraft Server",
    "hostname": "alpha.minecraft.server.com",
    "port": 25565,
    "local": true,
    "whitelist_path": "/srv/minecraft/alpha/whitelist.json",
    "systemctl_name": "minecraft",
    "systemctl_ext": "alpha"
  },
  {
    "name": "Hypixel",
    "hostname": "mc.hypixel.net",
    "port": 25565,
    "local": false
  }
]
```

Values:

- `name`: The pretty name visible by default to commands like /status.
- `hostname`: The ip address of the server (can use localhost, but it wont display the external facing ip when you ask for it)
- `port`: The port the server is running on, will be displayed if is non default when prompted for the hostname.
- `local`: True if this server is local
- `whitelist_path`: Path to the whitelist.json file for this local server
- `systemctl_name`: Service name of the server (ie minecraft@.service => `systemctl_name=minecraft`)
- `systemctl_ext`: Name of the specific minecraft server (ie minecraft@vanilla.service => `systemctl_ext=vanilla`). The service has been setup this way so you can easily run multiple minecraft servers.
- `default`: If this is the default active server for the bot.

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

### Local setup

As mentioned earlier, for the bot to have control over the server it has be run locally (on the same computer) and the server needs to be setup as described below.

This isn't neccessary if you only want the whitelist functionality though, as that directly edits your whitelist.json for simplicity.

In the below setup we let `servername` be the name of the server (one_word). Note that this is the value to use in the host config file for `systemctl_ext`. If there are multiple servers on the local system you want to manage with the bot make sure the names are different...

These systemd files are largely taken from [here](https://github.com/jtait/minecraft_systemd/tree/master) if you want to read their setup instructions.

#### Minecraft files

Minecraft server files should be moved to the `/srv/` directory. make the directory `/srv/minecraft` and then put your server folder in there. So the path to server `servername` would be `/srv/minecraft/servername`. Also make sure the minecraft directory is owned by your minecraft admin account and group.

#### systemd

We now want to make a service file, to launch our tmux session and start the minecraft server. Create the below files:

- `/etc/systemd/minecraft@.service`:

  A service file to let systemd know what to do.

  `User` and `Group` should be set to your minecraft admin account.

  ```
  [Unit]
  Description=Launch a Minecraft server in a tmux session
  After=local-fs.target network.target

  [Service]
  WorkingDirectory=/home/mineadmin/minecraft/server
  User=mineadmin
  Group=mineadmin
  Type=oneshot
  ExecStart=/script/launch.sh
  RemainAfterExit=true
  ExecStop=/bin/bash -c "tmux send-keys -t minecraft stop Enter && export PID=`cat server.pid` && while ps -p $PID > /dev/null; do sleep 1; done && tmux kill-session -t minecraft"
  StandardOutput=journal

  [Install]
  WantedBy=multi-user.target
  ```

- `/etc/systemd/system/minecraft@.socket`:
  socket systemd file that allows us to send commands to the minecraft server

  ```
  [Unit]
  Description=Minecraft server console socket
  BindsTo=minecraft@%i.service

  [Socket]
  ListenFIFO=/srv/minecraft/%i/systemd.stdin
  Service=minecraft@%i.service
  SocketUser=mineadmin
  SocketGroup=mineadmin
  RemoveOnStop=true
  SocketMode=0600

  [Install]
  WantedBy = sockets.target
  ```

After properly setting up these files the server can be started with `systemctl start minecraft@servername` and stopped with `systemct stop minecraft@servername`. To start the server automatically whenever the computer is on run `systemctl enable minecraft@servername`. This only needs to be done once

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
