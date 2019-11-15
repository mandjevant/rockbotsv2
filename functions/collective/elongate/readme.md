# elongate bot

Checks image dimensions and flairs an image submission with either 'Long' or 'Wide'.

## Setup and run

1. `cd functions/individual/elongate/`
2. `virtualenv env`
3. `source env/bin/activate`
4. `pip3 install -r requirements.txt`
5. `python3 elongate.py`

NOTE: **USE pip3 and python3 instead of pip and python**

## Parameters

Inside `config.py` file the following parameters are **necessary**:

- `self.id`: App id for your Reddit bot. See [here](https://www.reddit.com/prefs/apps/). Create a bot if you haven't.
- `self.secret`: App secret for Reddit bot.
- `self.username`: Your username
- `self.password`: Your password

These parameters are **customizable** in `config.py`:

- `user_agent`

***Do not change the value of other parameters***
