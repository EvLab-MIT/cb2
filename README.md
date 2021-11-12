Cereal Bar V2
============

- [Cereal Bar V2](#cereal-bar-v2)
  - [Intro](#intro)
  - [Setup](#setup)
    - [Cloning the repository.](#cloning-the-repository)
    - [Download Submodules](#download-submodules)
    - [Server](#server)
    - [Client](#client)
  - [Deploying a WebGL Client](#deploying-a-webgl-client)
  - [Server Endpoints](#server-endpoints)
  - [Resources](#resources)

Intro
-----

Cereal Bar is a two-player web game designed for studying language
understanding agents in collaborative interactions. This repository contains
code for the game, a webapp hosting the game, and various related tools.

This is a remake of the original Cereal Bar, which can be found [here][0]

Setup
-----

### Cloning the repository.

This repository uses [git-lfs][1]. Newer versions of git (>= 2.3.0) should handle this automatically, but for older versions you'll need to use `git lfs clone` when cloning this repository.

### Download Submodules

This repository contains a submodule. As such, you need to run this step to fetch submodules:

```
cd repo
git submodule init
git submodule update
```

### Server 

We recommend you setup a separate virtual environment for the server. Here's a quick intro:

* Create the venv with: `python3 -m venv <env_name>` (run once).
* Enter the venv with: `source <env_name>/bin/activate`
* Now that you're in a virtual python environment, you can proceed below to install the server requirements & run the server.
* Exit the venv with: `deactivate`
* Delete the venv by deleting the <env_name> directory generated by the first command.

The server is written in Python. Dependencies can be installed with:

```python3 -m pip install -r requirements.txt```

Then, you can launch the server:

```python3 -m main```

### Client

The client is a Unity project developed using `Version 2020.3.19f1`. This is contained in the `game/` directory. No setup should be necessary, just open the project in Unity.

Deploying a WebGL Client
------------------------

For development purposes, the server may be run locally and the client run directly in the Unity editor. For deployment, the game is compiled to Web Assembly and WebGL is used for efficient graphics in the browser. You can deploy a new version of the client by running:

```
./build_and_deploy.sh # Unity must be closed when running this.
```

This launches a headless version of Unity which builds a WebGL client and moves it to the appropriate directory (`server/www/WebGL`) in the server.

Upon completion of this command, one may launch the server and access the client via ```0.0.0.0:8080/WebGL/index.html```. The old build of the client is preserved at  `server/www/OLD_WebGL`.

[0]: https://github.com/lil-lab/cerealbar
[1]: https://git-lfs.github.com

Server Endpoints
----------------

| Endpoint URL         | Description                                           |
| -------------------- | ----------------------------------------------------- |
| `/`                  | Serves static files from `server/www`.                |
| `/status`            | Prints server status in JSON.                         |
| `/player_endpoint`   | Websocket endpoint for communication with clients.    |
| `/assets/{asset_id}` | Currently unused mechanism to obscurely serve assets. |

Resources
---------

`resources.txt`: Links to resources that were useful in development of this game.

`guidelines.txt`: Guiding thoughts on style, code review, and source code management. Always up for generous interpretation and change.