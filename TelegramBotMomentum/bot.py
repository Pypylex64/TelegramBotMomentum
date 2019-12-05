import telebot
import config 

bot = telebot.TeleBot(config.TOKEN)
print(bot.get_me())
