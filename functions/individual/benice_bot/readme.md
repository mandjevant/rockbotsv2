# benice bot

Randomly comments and awards gold to comments and submissions.

NOTE: **This bot requires customization**

## Setup and run

1. `cd functions/individual/BeNiceBot/`
2. `virtualenv env`
3. `source env/bin/activate`
4. `pip3 install -r requirements.txt`
5. `python3 benice.py`

NOTE: **USE pip3 and python3 instead of pip and python**

## Parameters

Inside `config.py` file the following parameters are **necessary**:

- `self.id`: App id for your Reddit bot. See [here](https://www.reddit.com/prefs/apps/). Create a bot if you haven't.
- `self.secret`: App secret for Reddit bot.
- `self.username`: Your username
- `self.password`: Your password

These parameters are **customizable** in `config.py`:

- `user_agent`
- `footer`
- `ping_response`
- `love_you_response`
- `good_bot_response`
- `bad_bot_resposne`
- `award_message`
- `silver_responses`
- `good_comments`
- `downvote_threshold`
- `golds_per_day`

***Do not change the value of other parameters***
