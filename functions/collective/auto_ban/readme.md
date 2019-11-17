# autoban

Takes strings or regex and the desired action when it is detected. 
Checks submission stream and/or comment stream for a match.

## Setup

Ensure your subreddit has 1 editable flair 'mod only'.

1. `cd functions/individual/auto_ban`
2. `virtualenv env`
3. `source env/bin/activate`
4. `pip install -r requirements.txt`

## Parameters

Inside `config.py` file the following parameters are **necessary**:

- `id`: App id for your Reddit bot. See [here](https://www.reddit.com/prefs/apps/). Create a bot if you haven't.
- `secret`: App secret for Reddit bot.
- `username`: Your username
- `password`: Your password
- `sub`: Your subreddit

These parameters are **customizable**:
- `user_agent`
- `rules`
- `checking`

***Do not change the value of other parameters***
