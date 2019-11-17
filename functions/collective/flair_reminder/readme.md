# flairbot

Reminds users to flair their submission. 
If the submission is not flaired in time, the submission will be removed.

## Setup

1. `cd functions/collective/flair_reminder`
2. `virtualenv env`
3. `source env/bin/activate`
4. `pip install -r requirements.txt`

## Parameters

Choose how the bot contacts the user;

| Python file | Type of reminder | Type of removal |
| --- | --- | --- |
| flairbot_all_comments.py | comment on submission | comment on submission |
| flairbot_all_messages.py | pm to submission author | pm to submission author |
| flairbot_flair_message_removal_comment.py | pm to submission author | comment on submission |

Inside `config.py` file the following parameters are **necessary**:

- `id`: App id for your Reddit bot. See [here](https://www.reddit.com/prefs/apps/). Create a bot if you haven't.
- `secret`: App secret for Reddit bot.
- `username`: Your username
- `password`: Your password

These parameters are **customizable**:
- `sub`
- `user_agent`
- `time_removal`
- `time_flair`
- `flair_message`
- `removal_message`
- `removal_title`

***Do not change the value of other parameters***
