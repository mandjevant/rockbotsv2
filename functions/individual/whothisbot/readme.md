# whothis bot

Looks for comments that contain the phrase "!whothis". Takes anyhting that comes after finds a summary of it from Wikipedia.
Summarizes to max 5 sentences.

## Setup and run

1. `cd functions/individual/whothisbot/`
2. `virtualenv env`
3. `source env/bin/activate`
4. `pip3 install -r requirements.txt`
5. `python3 whothis.py`

NOTE: **USE pip3 and python3 instead of pip and python**

## Parameters

Inside `config.py` file the following parameters are **necessary**:

- `self.id`: App id for your Reddit bot. See [here](https://www.reddit.com/prefs/apps/). Create a bot if you haven't.
- `self.secret`: App secret for Reddit bot.
- `self.username`: Your username
- `self.password`: Your password

These parameters are **customizable** in `config.py`:

- `helpmsg`

***Do not change the value of other parameters***
