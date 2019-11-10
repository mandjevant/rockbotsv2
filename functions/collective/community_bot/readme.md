# community bot

Comments on each submission, removes if downvote threshold is reached, edits body if upvote threshold is reached.

The functions:
- `!lock [reason]`
- `!remove [reason]`
- `!comment [reason]`

Are available. Just comment anywhere on the submission and the bot will do the rest.

## Setup

1. `cd functions/collective/community_bot`
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
- `sub`
- `threshold`
- `downvotethreshold`
- `comment_message`
- `removal_message`
- `removal_title`
- `removal_type`
- `upvote_threshold_message`
- `database_name`

***Do not change the value of other parameters***