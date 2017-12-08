#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Simple Bot to read private Advent of Code 2017 leaderboards.
# This program is dedicated to the public domain under the CC0 license.
Run `cat api_key.txt | python bot.py` to run the bot.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

"""

from telegram.ext import Updater, CommandHandler
import logging
import requests
import json
from pprint import pprint
from operator import itemgetter
import datetime
from dateutil import parser
import sys

leaderboard_url_format = "https://adventofcode.com/2017/leaderboard/private/view/%s.json"

cookies = dict(
    session='')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text('Hi, I\'m a leaderboard bot for Advent of Code 2017!\nUsage:\n\t/set <leaderboard_nr> <session_cookie>\n\t/get: shows leaderboards')

def set_data(bot, update, args, chat_data):
    chat_id = update.message.chat_id
    leaderboard_id = args[0]
    session_cookie = args[1]

    chat_data['chat_id'] = chat_id
    chat_data['leaderboard_id'] = leaderboard_id
    chat_data['session_cookie'] = session_cookie
    update.message.reply_text('Leaderboard id and session cookie set.')

def retrieve_leaderboard(leaderboard_id, session_cookie):
    r = requests.get(leaderboard_url_format % (leaderboard_id), cookies=dict(
        session=session_cookie))
    if not r.ok:
        raise ValueError("Invalid leaderboard id or session cookie.")
    r_json = json.loads(r.text)

    members = []

    for member in r_json.get('members'):
        members.append(member)

    score_dictionary = {}

    # newest_timestamp = datetime.datetime(
    #     2000, 1, 1, tzinfo=datetime.timezone.utc)
    # for member in members:
    #     data = r_json.get('members', {}).get(
    #         member, {}).get('completion_day_level', {})
    #     for day in data.items():
    #         stars = day[1]
    #         for star in stars.items():
    #             timestamp_part = star[1]
    #             ts_string = timestamp_part['get_star_ts']

    #             time = parser.parse(ts_string)
    #             newest_timestamp = max(newest_timestamp, time)
    # current_time_with_offset = datetime.datetime.now(
    #     datetime.timezone.utc) - datetime.timedelta(seconds=1000)

    # if newest_timestamp < current_time_with_offset:
    #     logger.info("No update needed")
    #     return

    for member in members:
        data = r_json.get('members', {}).get(member, {})
        score_dictionary[data.get('name')] = data.get('local_score')

    sorted_dict = sorted(score_dictionary.items(),
                         key=itemgetter(1), reverse=True)
    return sorted_dict


def get(bot, update, chat_data):
    try:
        leaderboard_id = chat_data['leaderboard_id']
        session_cookie = chat_data['session_cookie']
    except KeyError:
        if not given_leaderboard_and_session_ids:
            update.message.reply_text(
                'Try setting a leaderboard and session id first.')
            return
        global leaderboard_id_global
        global session_cookie_global
        leaderboard_id = leaderboard_id_global
        session_cookie = session_cookie_global
        chat_data['leaderboard_id'] = leaderboard_id
        chat_data['session_cookie'] = session_cookie


    try:
        leaderboard = retrieve_leaderboard(leaderboard_id, session_cookie)
    except ValueError:
        update.message.reply_text(
            'You might have set a wrong leaderboard or session id.')
        return

    text_to_send = "Leaderboard %s:\n" % (leaderboard_id)
    for item in leaderboard:
        player_name = item[0]
        player_score = item[1]
        # print(player_score, player_name)
        text_to_send += ("%s %s\n" % (player_score, player_name))

    update.message.reply_text(text_to_send)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

given_leaderboard_and_session_ids = False
leaderboard_id_global = ""
session_cookie_global = ""

def main():
    """Run bot."""
    lines = sys.stdin.read().splitlines()
    api_key = lines[0]
    try:
        global given_leaderboard_and_session_ids
        global leaderboard_id_global
        global session_cookie_global
        leaderboard_id = lines[1]
        session_cookie = lines[2]
        given_leaderboard_and_session_ids = True
        leaderboard_id_global = leaderboard_id
        session_cookie_global = session_cookie
        logger.info("Using given leaderboard id and session id as default")
    except IndexError:
        logger.info("No leaderboard id and session id given, letting user set that")
    # logger.info("API key:%s" % (api_key))

    updater = Updater(api_key)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("set", set_data,
                                  pass_args=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("get", get,
                                pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    logger.info("Bot started")

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
