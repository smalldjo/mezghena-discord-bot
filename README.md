# Mezghena Discord Bot:
### a discord bot based on [discord.py](https://github.com/Rapptz/discord.py) aimed at offering useful commands for Algerian discord servers.


## what does Mezghena offer:
- **a "translate" command:**
  - translate words between English and Algerian Arabic (Derja) using [glosbe.com API](https://glosbe.com/arq)
- **a "trends" command:**
  - display trending content in Algeria on Youtube & Twitter
- **support  for introduction channels:**
  - let the bot manages a chosen channel as an introduction channel by controlling the number of the introductions per user and their length.
  - a "who" command that displays basic infos about users with their introduction if given.
- **a flags game:**
  - guess the country from its flag, play against other users, collect more points to win.

 and more to come.


## How to run:
Python 3+ and a postgresql database are required to run this bot.

once you got those clone this repo:

`git clone https://github.com/smalldjo/mazghena-discord-bot.git mezghena`

if you don't have virtualenv install it throught:

` apt-get install virtualenv`

create a virtual environment

```
cd mezghena
virtualenv venv --python=python3.6
```
activate it

`source venv/bin/activate`

with the virtual env activated install requirements through pip:

`pip install -r requirements.txt `

create a postgresql database and set its owner to the user you want.

open `mezghena/Config.py` and fill these vars:

```
#####################
##### DB infos: #####
#####################

DB_name = ""
DB_user = ""
DB_password = ""

```

now you need to create a discord app for the bot [here](https://discordapp.com/developers)

you also need a [Youtube API Key](https://console.developers.google.com) (create app and add  YouTube Data API v3 service)

and a [twitter app](https://apps.twitter.com/)

once you have the keys/tokens open `mazghena/private/tokens.py` and put them in their respective vars:

```
#discord app client secret:
DISCORD_API_KEY = ''


YOUTUBE_DATA_TOKEN = ''

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_ACCESS_KEY = ''
TWITTER_ACCESS_SECRET = ''
```


 run the bot with:
`python main.py`

the bot should be running, you need to invite it to a server so you can actually interact with it

to do that use this link:

https://discordapp.com/api/oauth2/authorize?client_id={DISCORD_APP_Client_ID}&scope=bot&permissions=73728
