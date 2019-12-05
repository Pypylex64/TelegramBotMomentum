from db import users_db
from bot import bot




if __name__ == '__main__':
   # Считываем сообщение с клавиатуры
   input_message = input('Введите сообщение для рассылки: ')
   send_message_to_all_users(input_message)
