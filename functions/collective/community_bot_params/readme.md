# communityparams bot

Lets users vote on submissions with the parameters 'insane', 'not insane' and 'fake'.
Acts after the voting is over which is most voted and acts accordingly.

Users can use 
- `!explanation` (Only OP)

And moderators can use:
- `!disable` (Only on bot comment)
- `!comment [reason]`
- `!remove [reason]`
- `!lock [reason]`
- `!hotline` or `!hotlines`

**This bot needs manual editing in config.py and insane.py since dynamicality is not fully pursued.**

## Setup

1. `cd functions/collective/community_bot_params`
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
- `sub`
- `user_agent`
- `initial_comment`
- `final_comment`
- `footer`
- `removal_type`
- `hotline`
- `maxtime`

***Do not change the value of other parameters***
