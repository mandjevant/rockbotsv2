# modqueuecounter

Counts the items in a queue. Maxes out at 1000 items.

## Setup

1. `cd functions/individual/modqueuecounter`
2. `virtualenv env`
3. `source env/bin/activate`
4. `pip install -r requirements.txt`

## Parameters

Inside `config.py` file the following parameters are **necessary**:

- `id`: App id for your Reddit bot. See [here](https://www.reddit.com/prefs/apps/). Create a bot if you haven't.
- `secret`: App secret for Reddit bot.
- `username`: Your username
- `password`: Your password

These parameters are **customizable**:
- `user_agent`

***Do not change the value of other parameters***