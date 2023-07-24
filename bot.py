import os

import telebot
import urllib3
from get_positions import get_positions

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['positions'])
def send_welcome(message):
    get_positions()
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()


# gets my positions and portfolio status 
# gets trending tokens
# gets tokens approaching support or resistance

# gets the current leaderboard and positions 
# @bot.message_handler(commands=['whales', 'hello'])