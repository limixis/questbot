# -*- coding: UTF-8 -*-

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import json

import argparse


TOKEN = ''
path = "./tasks.json"

# markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

ADMIN_NAMES = ['limixis']


def parse_args():
    parser = argparse.ArgumentParser(description="Generate tokens for authentication")
    parser.add_argument("-f", dest="quest_path", default="./tasks.json", help="Path to json file with tasks")

    return parser.parse_args()


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=u'Привет! Пора пройти квест...')


class Chatter(object):
    def __init__(self, path):
        self.modes = {'start': self.on_start, 'answer': self.on_answer}
        with open(path) as f:
            self.quest = json.load(f)

    def handle_update(self, bot, update, user_data):
        if not user_data.get('stage'):
            user_data['stage'] = 0
        if not user_data.get('answer'):
            user_data['answer'] = 'start'
        func = self.modes[user_data['answer']]
        func(bot, update, user_data)

    def on_start(self, bot, update, user_data):
        task_start = self.quest[user_data['stage']].get("on_start")
        fields = task_start.get("fields")
        for field in fields:
            message = task_start.get(field)
            keyboard = task_start.get("keyboard")
            markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id, text=message, reply_markup=markup)

    def on_answer(self, bot, update, user_data):
        task = self.quest[user_data['stage']]
        answer = update.message.text.lower().strip()
        is_correct = (answer == task.get("correct_answer"))
        branch = 'on_correct_answer' if is_correct else 'on_incorrect_answer'
        task_branch = task.get(branch)
        fields = task_branch.get("fields")
        for field in fields:
            message = task_branch.get(field)
            keyboard = task_branch.get("keyboard")
            markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id, text=message, reply_markup=markup)



if __name__ == "__main__":

    # If you want to pass parameters via command line
    # args = parse_args()
    # path = args.quest_path

    updater = Updater(token=TOKEN)

    dp = updater.dispatcher

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    start_handler = CommandHandler('start', start)
    dp.add_handler(start_handler)

    chatter = Chatter(path)
    text_handler = MessageHandler(Filters.text, chatter.handle_update, pass_user_data=True)
    dp.add_handler(text_handler)

    updater.start_polling()

    updater.idle()
