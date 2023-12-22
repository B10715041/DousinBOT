# Discord Bot for VNDB Queries

## Introduction
This Discord bot was developed as a personal project to get more familiar with Neovim plugins and the Git tool. The bot serves as a practical application for enhancing my workflow in software development and understanding version control systems more deeply.

## Bot Features
The bot offers a range of functionalities to enhance user interaction and engagement on Discord servers. It is specifically tailored for querying the Visual Novel Database (VNDB) and providing quick responses within Discord chats. The bot is built using Python and the discord.py library, ensuring smooth integration and performance.

### Commands and Usage
The bot uses `!` as the command prefix. Below is a list of available commands:

- `!echo [message]`: Echoes the message sent by the user.
- `!clear [number]`: Deletes the specified number of messages from the chat.
- `!help`: Displays a help message listing all the available commands and their usage.
- `?[search term]`: When a message starts with `?`, the bot interprets it as a search query for VNDB. The bot will return information about the visual novel matching the search term.

### VNDB Query Feature
The bot can query the VNDB API for information about visual novels. Users can simply type `?[search term]` to trigger a search. The bot responds with detailed information about the visual novel, including title, aliases, developer, release date, length, rating, vote count, and a link to the VNDB page. It also provides information about voice actors and staff involved in the visual novel.


