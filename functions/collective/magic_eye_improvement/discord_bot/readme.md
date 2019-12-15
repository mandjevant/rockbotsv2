# magic eye improvement | Discord

Posts images and submission link of possible magic eye mistakes in a discord channel.

Has additional commands like:
- `$revert` | Reverts magic eye actions
- `$down` | Checks if your flair bot and community bot are online
- `$approve [USERNAME]` | Adds user to approved users in your sub

## Setup

1. `cd functions/collective/magic_eye_improvement/discord_bot`
2. `virtualenv env`
3. `source env/bin/activate`
4. `pip install -r requirements.txt`

## Parameters

Inside `config.py` file the following parameters are **necessary**:

- `id`: App id for your Reddit bot. See [here](https://www.reddit.com/prefs/apps/). Create a bot if you haven't.
- `secret`: App secret for Reddit bot.
- `username`: Your username
- `password`: Your password
- `discord_id`: Your discord Token. See [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token) Create a Token if you haven't.

These parameters are **customizable**:
- `user_agent`
- `sub`
- `bot_username`
- `bot_username_2`

***Do not change the value of other parameters***