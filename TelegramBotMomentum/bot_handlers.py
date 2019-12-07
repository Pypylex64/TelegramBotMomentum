from bot import bot 
from messages import * 
from db import users_db, client
from telebot import types
from config import CHAT_ID_ADMIN


def keyboard_main_menu(message):
    "Главное меню с кнопками для взаимодействия с пользователем"
    button_change_name = types.KeyboardButton("Изменить имя")
    button_change_gender = types.KeyboardButton("Изменить пол")
    button_change_age = types.KeyboardButton("Изменить возраст")
    keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_main.add(button_change_name)
    keyboard_main.add(button_change_gender)
    keyboard_main.add(button_change_age)

    # Привелегии админа для рассылки писем
    if message.chat.id == CHAT_ID_ADMIN:
        button_mailing = types.KeyboardButton("Рассылка")
        keyboard_main.add(button_mailing)
        
    return keyboard_main


@bot.message_handler(commands=["start"])
def start_bot(message):
    "Получаем информацию о пользователе"
    if not users_db.find_one({"chat_id": message.chat.id}):
        users_db.insert_one({"chat_id" : message.chat.id})
        
        # Приветствие и запрос имени
        bot.send_message(message.chat.id, HELLO)
        bot.send_message(message.chat.id, NAME)
        
        # Следующий шаг - функция 
        bot.register_next_step_handler(message, get_name)
    else:

        msg = bot.send_message(message.chat.id, BACK, reply_markup=keyboard_main_menu(message))
        bot.register_next_step_handler(msg, main_menu)


def get_name(message):
    "Получаем имя пользователя для добавления его в бд"
    username = str(message.text)

    # Сохраняем имя 
    username = username.title()

    users_db.update({"chat_id": message.chat.id}, {"$set": {"name": username}})
    bot.send_message(message.chat.id, CORECT_NAME)

    # Задаем вопрос о гендере
    # Создадим клавиатуру
    button_m = types.KeyboardButton("M")
    button_g = types.KeyboardButton("Ж")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(button_g, button_m)
    msg = bot.send_message(message.chat.id, GENDER, reply_markup=markup)

    # Передаем задачу следующей функции
    bot.register_next_step_handler(msg, get_gender)


def get_gender(message):
    "Узнаем пол пользователя и для сохранения в бд"
    user_gender = str(message.text)
    users_db.update({"chat_id": message.chat.id}, {"$set": {"gender": user_gender}})

    # Вопрос о возрасте
    bot.send_message(message.chat.id, AGE)
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    "Узнаем корректный возраст пользователя для сохранения в бд"
    try:
        user_age = int(message.text)
        users_db.update({"chat_id": message.chat.id}, {"$set": {"age": user_age}})
        msg = bot.send_message(message.chat.id, END, reply_markup=keyboard_main_menu(message))
    except TypeError:
        # Выводим сообщение об ошибке
        msg = bot.send_message(message.chat.id, ERROR_AGE, reply_markup=keyboard_main_menu(message))
        
    
    # Показываем главное меню
    bot.register_next_step_handler(message, main_menu)


@bot.message_handler(content_types=['text'])
def main_menu(message):
    "Обрабатываем ответы на нажатие кнопок"
    button_message = str(message.text)

    # Добавим кнопку назад
    back_button = types.KeyboardButton("Назад")
    keyboard_back = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard_back.add(back_button)
    
    if button_message.lower() == "изменить имя":
        msg = bot.send_message(message.chat.id, NAME, reply_markup=keyboard_back)

        # Обрабатываем событие change_name 
        bot.register_next_step_handler(msg, change_name)
        
    if button_message.lower() == "изменить пол": 
        # Задаем вопрос о смене гендера
        button_m = types.KeyboardButton("M")
        button_g = types.KeyboardButton("Ж")
        markup_gender = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup_gender.row(button_g, button_m, back_button)
        
        msg = bot.send_message(message.chat.id, GENDER, reply_markup=markup_gender)
        
        # Обрабатываем событие change_gender 
        bot.register_next_step_handler(msg, change_gender)
        
    if button_message.lower() == "изменить возраст":
        # Задаем вопрос о смене возрасте
        msg = bot.send_message(message.chat.id, AGE, reply_markup=keyboard_back)

        # Обрабатываем событие change_age
        bot.register_next_step_handler(msg, change_age)

    if button_message.lower() == "рассылка":
        # Принимаем сообщение которое надо разослать
        msg = bot.send_message(message.chat.id, ADMIN, reply_markup=keyboard_back)

        # Обрабатываем событие send_message_to_all_users
        bot.register_next_step_handler(msg, send_message_to_all_users)

    else:
        # Возвращаем меню при любом другом тексте
        bot.register_next_step_handler(message, main_menu)


def change_name(message):
    "Меняет имя и/или возвращет на главное меню"
    message_str = str(message.text)
    if message_str.lower() == 'назад':
        # Не забываем про кнопку назад
        msg = bot.send_message(message.chat.id, BACK, reply_markup=keyboard_main_menu(message))
        bot.register_next_step_handler(message, main_menu)
        
    else:
        # Сохраняем имя 
        message_str = message_str.title()
        users_db.update({"chat_id": message.chat.id}, {"$set": {"name": message_str}})
        msg = bot.send_message(message.chat.id, CORECT_NAME, reply_markup=keyboard_main_menu(message))
        bot.register_next_step_handler(msg, main_menu)


def change_gender(message):
    "Меняет пол и/или возвращает на главное меню"
    message_str = str(message.text)
    if message_str.lower() == 'назад':
        msg = bot.send_message(message.chat.id, BACK, reply_markup=keyboard_main_menu(message))
        bot.register_next_step_handler(msg, main_menu)
    else:
        users_db.update({"chat_id": message.chat.id}, {"$set": {"gender": message_str}})
        msg = bot.send_message(message.chat.id, CORECT_GENDER, reply_markup=keyboard_main_menu(message))
        bot.register_next_step_handler(msg, main_menu)


def change_age(message):
    "Меняет возраст и/или возвращает на главное меню"
    message_str = str(message.text)
    if message_str.lower() == 'назад':
        msg = bot.send_message(message.chat.id, BACK, reply_markup=keyboard_main_menu(message))
        bot.register_next_step_handler(msg, main_menu)
    else:
        try:
            user = users_db.find_one({"chat_id": message.chat.id})
            message_int = int(message_str)
            if message_int != user["age"]:
                users_db.update({"chat_id": message.chat.id}, {"$set": {"age": message_int}})
                
                # Показываем главное меню
                msg = bot.send_message(message.chat.id, AGE_CORECT, reply_markup=keyboard_main_menu(message))
                
            else:
                msg = bot.send_message(message.chat.id, AGE_REPEAT, reply_markup=keyboard_main_menu(message))
            
            bot.register_next_step_handler(msg, main_menu)
        except TypeError:
            # Просим ввести корректное возраст
            msg = bot.send_message(message.chat.id, ERROR_AGE, reply_markup=keyboard_main_menu(message))
            bot.register_next_step_handler(msg, main_menu)


def send_message_to_all_users(message):
    "Функция для рассылки, принимает сообщение"
    message_admin = str(message.text)
    if message_admin.lower() == 'назад':
        # Не забываем про кнопку назад
        msg = bot.send_message(message.chat.id, BACK, reply_markup=keyboard_main_menu(message))
        bot.register_next_step_handler(msg, main_menu)
    if message_admin != '':
        # Перебираем всех пользователей в бд
        for user in users_db.find():
            # Пытаемся отправить сообщение
            try:
                bot.send_message(user['chat_id'], message_admin)
            except Exception as e:
                bot.send_message(user[CHAT_ID_ADMIN], ERROR_MAIL)

        # Возвращаемся в главное меню
        msg = bot.send_message(user[CHAT_ID_ADMIN], MAILING, reply_markup=keyboard_main_menu(message))
        bot.register_next_step_handler(msg, main_menu)
    else:
        # Возвращаемся в главное меню
        msg = bot.send_message(user[CHAT_ID_ADMIN], NOT_CORECT_MAIL, reply_markup=keyboard_main_menu(message))
        bot.register_next_step_handler(msg, main_menu)


if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling(none_stop=True)
