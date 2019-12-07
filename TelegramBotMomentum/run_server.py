import os
from flask import Flask, request
from telebot import types
from config import *
from bot_handlers import bot


server = Flask(__name__)


if bot.get_webhook_info().url != 'https://{}.herokuapp.com/{}'.format(APP_NAME, TOKEN):
    bot.remove_webhook()
    bot.set_webhook(url='https://{}.herokuapp.com/{}'.format(APP_NAME, TOKEN))


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200


@server.route('/', methods=['GET'])
def index():
    return 'Home page', 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
