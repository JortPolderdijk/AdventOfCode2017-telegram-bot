# Advent of Code 2017 Telegram bot

Telegram bot which shows a private AoC leaderboard on request (/get).

## Usage

Install dependencies:

* `pip install -r requirements.txt`

Run the bot:

* `cat api_key | ./bot.py` Run the bot without default leaderboard and session cookie (recommended)
* `cat bot_info | ./bot.py` Run the bot with a default leaderboard and session cookie

Telegram commands:

* `/set <leaderboard_id> <session_cookie>` Sets the leaderboard id and session cookie
* `/get` Shows the leaderboard, sorted on highest score
