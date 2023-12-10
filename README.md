# Minecraft-Telegram-bot

## About

This is a basic server telegram bot that can interface with minecraft servers in a couple of ways:

- ping public facing servers and get info
- control local minecraft server
- control local whitelist.json files
- telegram users can link their account to their minecraft account, allowing telegram messages to be forwarded to mc chat.
- TODO control local blacklist.json files?
- TODO control server.properties settings?

This bot is not a plugin or a mod, it is a standalone python program. If setup local to your minecraft servers it'll have access to their consoles through a FIFO file (see setup instructions and details below). This also means that it could be used for basically any version of minecraft. I plan to use it to manage 3 servers of differing versions at once.

## Interface overview

There are some nice visuals the bot provides:

- The `/status` command mimics the minecraft launcher, rendered using the `html2image` package:
  ![hypixel example image](public/hypixel.jpg)
- The `/whitelistadd` command renders the user's skin with [NickAc's Minecraft Skin Renderer](https://nmsr.nickac.dev/) so you can be sure you've added the right person:
  <img src="public/whitelist.png" data-canonical-src="public/whitelist.png" width="200"/>
- The `/online` command renders the user faces + names like a tablist, using the `htm2image`. #TODO get an example image of this.
- Telegram messages forwarded to minecraft chat (from linked users in the configured) support near full formatting (bold, italic, underline, strikethrough, spoiler,)

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
    "version": "1.20.4",
    "port": 25565,
    "local": true,
    "whitelist_path": "/srv/minecraft/vanilla/whitelist.json",
    "systemctl_name": "minecraft",
    "extname": "vanilla",
    "alpha": true,
    "default": true
  },
  {
    "name": "My Minecraft Server",
    "hostname": "alpha.minecraft.server.com",
    "version": "a1.2.6",
    "port": 25565,
    "local": true,
    "whitelist_path": "/srv/minecraft/alpha/whitelist.json",
    "systemctl_name": "minecraft",
    "extname": "alpha",
    "alpha": false,
    "default": false
  },
  {
    "name": "Hypixel",
    "hostname": "mc.hypixel.net",
    "version": "1.8-1.20.4",
    "port": 25565,
    "local": false,
    "whitelist_path": null,
    "systemctl_name": null,
    "extname": null,
    "alpha": false,
    "default": false
  }
]
```

Values:

- `name`: The pretty name visible by default to commands like /status.
- `hostname`: The ip address of the server (can use localhost, but it wont display the external facing ip when you ask for it)
- `version`: The version or versions supported by the server. Standard minecraft version format seperated by commas for a list, or a hyphen for a range. ie: "1.8.0-1.20.4" or "1.18.1,1.18.2"
- `port`: The port the server is running on, will be displayed if is non default when prompted for the hostname.
- `local`: True if this server is local
- `whitelist_path`: Path to the whitelist.json file for this local server. Could phase this out and use extname to find it, but that would only work if one decides to fully integrade with the bot.
- `systemctl_name`: Service name of the server (ie minecraft@.service => `systemctl_name=minecraft`)
- `extname`: Name of the specific minecraft server (ie minecraft@vanilla.service => `extname=vanilla`). The service has been setup this way so you can easily run multiple minecraft servers. This is also the short name you will use when refrencing the host (hostname can be used, but they are generally long)
- `alpha`: If the server is an alpha/beta server which will not respond to modern minecraft pings. (TODO phase this away with the versioning)
- `default`: If this is the default active server for the bot.

### .env

```bash
# telegram bot config, required
DEVELOPER_CHAT_ID = "DEV_CHAT_ID"
MINECRAFT_CHAT_ID = ""
TOKEN             = "TELEGRAM_BOT_TOKEN"

# admin config, optional
ADMINS = '[]'
MOCK_STICKERS = '[]'

# dev config
ENV = "develop"
```

Values:

- `DEVELOPER_CHAT_ID`: chat id where you want errors sent
- `MINECRAFT_CHAT_ID`: The main telegram chat that the bot will be operating in. TODO: make this a list? or a config file?
- `TOKEN`: telegram bot token
- `ADMINS`: a json list of the admins you wish to give hard coded access
- `MOCK_STICKERS`: list of sticker ids that can be sent when a non admin tries to use an admin command
- `ENV`: current enviroment, if "develop" some operations will be logged into console rather than executed (ie testing from non server computer)

### Local setup

As mentioned earlier, for the bot to have control over the server it has be run locally (on the same computer) and the server needs to be setup as described below.

This isn't neccessary if you only want the whitelist functionality though, as that directly edits your whitelist.json for simplicity.

In the below setup we let `servername` be the name of the server (one_word). Note that this is the value to use in the host config file for `extname`. If there are multiple servers on the local system you want to manage with the bot make sure the names are different...

These systemd files are largely taken from [here](https://github.com/jtait/minecraft_systemd/tree/master) if you want to read their setup instructions.

#### Minecraft files

Minecraft server files should be moved to the `/srv/` directory. make the directory `/srv/minecraft` and then put your server folder in there. So the path to server `servername` would be `/srv/minecraft/servername`. Also make sure the minecraft directory is owned by your minecraft admin account and group.

#### systemd

We now want to make the following service files to launch our minecraft servers:

- `/etc/systemd/minecraft@.service`:

  A service file to let systemd know what to do, actually runs the server.

  `User` and `Group` should be set to your minecraft admin account.

  ```
  [Unit]
  Description=Minecraft Server - %i
  After=local-fs.target network.target
  ConditionPathExists=/srv/minecraft/%i

  [Service]
  WorkingDirectory=/srv/minecraft/%i

  Sockets=minecraft@%i.socket
  StandardInput=socket
  StandardOutput=journal
  StandardError=journal

  User=mineadmin
  Group=mineadmin

  Environment="MIN_MEM=1024M"
  Environment="MAX_MEM=4G"
  Environment="JAR_PATH=server.jar"
  Environment="JAVA_PARAMETERS="

  EnviromentFile=/srv/minecraft/%i/systemd.conf

  ExecStart=/bin/sh -c "/usr/bin/java -server -Xms${MIN_MEM} -Xmx${MAX_MEM} ${JAVA_PARAMETERS} -jar >
  ExecStop=/bin/sh -c "/bin/echo stop > /srv/minecraft/%i/systemd.stdin"
  Restart=on-failure
  RestartSec=60s

  KillSignal=SIGCONT

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

- `/status [hostname...] -a,--all -h,--hostname`
  Check server(s) status, renders motd like in the minecraft launcher.
  - -a, --all: show all of the hosts in your hosts file.
  - -h, --hostname: show hostnames instead of pretty names.
- `/ping [hostname]`:
  Measure the response time of the server.
- `/online [hostname]`:
  Check what players are online (obsfucated by some servers)
- `/link <username>`:
  Link your telegram user to your minecraft user. Afer linking, your telegram messages will be sent to the online minecraft servers in chat.

### Admin commands

- `/activate [extname]`
  Select the active server by it's extname, or send what the active host is
- `/serverstop [extname]`:
  Stop the server, defaults to active server
- `/serverstart [extname]`:
  Start the server, defaults to active server
- `/serverrestart [extname]`:
  Restart the server, defaults to active server
- `/whitelistadd <username> [extname]`:
  Add player to the whitelist of the active server
- `/whitelistrm <username> [extname]`:
  Remove player from the whitelist
- `/activate <hostname>`:
  Set active server for general commands
- `/local`:
  list local server information: extnames, hostnames, whitelist status

### General admin commands:

Additionally, any command you send that is not one of the above (like /say) is sent to the server console. This way you can do more complicated things if needed. TODO support command output from the services.
