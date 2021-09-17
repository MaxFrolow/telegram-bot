import telebot
import psycopg2
from psycopg2.extras import DictCursor
import bot_settings
from datetime import datetime
from db_process import DbProcessor
from telebot import types
import random
import string
from datetime import datetime
#--------------------------------------------------------
# Main Processors
#-------------------------------------------------------
bot = telebot.TeleBot(bot_settings.telegram_bot_token)
DBP = DbProcessor


#--------------------------------------------------------
# Test vars
#-------------------------------------------------------


rooms = {123456:"123456",
         111111:"111111"}


day_bal = 300
mon_bal = 2000
day_in = 200
mon_in = 1000
date_last = ""
date_now = ""
datem_last = ""
datem_now = ""
password = "123456"
room_home="123456"
room_current="123456"
help_text ="""
Завантажено базові команди
Спочатку потрібно налаштувати бота: /setup

Налаштування:
Показані дані для твоєї кімнати.
Для того що б долучитися до іншої кімнати, спитай домашню кімнату власника і пароль.
Далі: /change_room і слідувати інструкціям.

Використання:
Будь яке число буде відніматися від денного балансу.
Для відняття від місячного балансу використати: 
/mon_bal
/start -> Баланс -> Місячна витрата
"""
#--------------------------------------------------------
# Messages handling
#-------------------------------------------------------

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # Если написали «Привет»
    try:
        
        
        if message.text == "/help":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('/start', 'Перевірити Баланс', '/setup', "/mon_bal")
            bot.send_message(message.from_user.id, text='Завантажено базові команди', reply_markup=markup)
        
        elif message.text == "/start":
            keyboard = types.InlineKeyboardMarkup()

            key_bal = types.InlineKeyboardButton(text='Баланс', callback_data='balance') 
            keyboard.add(key_bal)

            key_setup = types.InlineKeyboardButton(text='Налаштування', callback_data='setup') 
            keyboard.add(key_setup)

            bot.send_message(message.from_user.id, text='Привіт, чим можу допомогти?', reply_markup=keyboard)
        
        elif message.text == "/setup":
            setup_menu(message)
        elif message.text == "Перевірити Баланс":
            balance(message)
        elif message.text == "/change_day":
            sent = bot.send_message(message.chat.id, 'Вкажи новий денний приріст')
            bot.register_next_step_handler(sent, set_day)
        
        elif message.text == "/change_mon":
            sent = bot.send_message(message.chat.id, 'Вкажи новий місячний приріст')
            bot.register_next_step_handler(sent, set_mon)
        
        elif message.text == "/change_room":
            sent = bot.send_message(message.chat.id, 'Вкажи нову кімнату у фарматі Номер_кімнати#пароль')
            bot.register_next_step_handler(sent, set_room)
        
        elif message.text == "/change_password":
            sent = bot.send_message(message.chat.id, 'Вкажи новий пароль')
            bot.register_next_step_handler(sent, set_pass)
        
        elif message.text == "/mon_bal":
            sent = bot.send_message(message.chat.id, 'Вкажи місячну витрату')
            bot.register_next_step_handler(sent, mon_bal_handler)
        
        elif type(int(message.text)) == int:
            day_bal_handler(message)
        
        else:
            bot.send_message(message.from_user.id, "Я тебя не розумію. Напиши /help.")
    except Exception as e:
        bot.send_message(message.from_user.id, "Main: {}".format(e))

#--------------------------------------------------------
#Callback
#-------------------------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "setup": 
        try:
            info = DBP.get_room_in(call.message.chat.id)
            if not info:
                password, room_id = password_generator()
                currentDay = datetime.now().strftime('%d')
                currentMonth = datetime.now().strftime('%m')
                DBP.save_data("rooms", 
                            "room_id, day_in, mon_in, day_bal, mon_bal, room_day_in, room_mon_in, password",
                            "{}, 300, 3000, 300, 3000, {}, {}, {}".format(room_id, currentDay, currentMonth, password))
                DBP.save_data("accounts", "user_id, room_current, room_home", "{}, {}, {}".format(call.message.chat.id, room_id, room_id))
            info = DBP.get_room_in(call.message.chat.id)
            bot.send_message(call.message.chat.id, "Info: {}".format(info))
        except Exception as e:
            bot.send_message(call.message.chat.id, e)
        bot.send_message(call.message.chat.id, """
Денний +: {0}   
Змінити /change_day

Міячний +: {1}  
Змінити /change_mon

Активна кімната: {2}
Змінити /change_room

Домашня кімната: {3}
Змінити пароль /change_password
""".format(info[0], info[1], info[2], info[3]))
    elif call.data == "balance":
        keyboard = types.InlineKeyboardMarkup()

        key_mon_bal = types.InlineKeyboardButton(text='Місячна витрата', callback_data='mon_bal')  
        keyboard.add(key_mon_bal)
        balance = DBP.get_bal(call.message.chat.id)
        bot.send_message(call.message.chat.id, text='Денний: {0}\nМіячний баланс: {1}'.format(balance[0], balance[1]), reply_markup=keyboard)

    elif call.data == "mon_bal":
        sent = sent = bot.send_message(call.message.chat.id, 'Вкажи витрату з місячного балансу')
        bot.register_next_step_handler(sent, mon_bal_handler)




#--------------------------------------------------------
#Main functions
#-------------------------------------------------------
def setup_menu(message_type):
    global day_in, mon_in
    try:
        info = DBP.get_room_in(message_type.chat.id)
        if not info:
            password, room_id = password_generator()
            currentDay = datetime.now().strftime('%d')
            currentMonth = datetime.now().strftime('%m')
            DBP.save_data("rooms", 
                          "room_id, day_in, mon_in, day_bal, mon_bal, room_day_in, room_mon_in, password",
                          "{}, 300, 3000, 300, 3000, {}, {}, {}".format(room_id, currentDay, currentMonth, password))
            DBP.save_data("accounts", "user_id, room_current, room_home", "{}, {}, {}".format(message_type.chat.id, room_id, room_id))
        info = DBP.get_room_in(message_type.chat.id)
        bot.send_message(message_type.chat.id, "Info: {}".format(info))
    except Exception as e:
        bot.send_message(message_type.chat.id, e)    
    bot.send_message(message_type.chat.id, """
Денний +: {0}   
Змінити /change_day

Міячний +: {1}  
Змінити /change_mon

Активна кімната: {2}
Змінити /change_room

Домашня кімната: {3}
Змінити пароль /change_password
""".format(info[0], info[1], info[2], info[3]))
def set_day(message):
    
    try:
        if type(int(message.text)) == int:
            info = str(DBP.get_data("accounts", "room_current", "user_id", message.from_user.id)[0])
            DBP.update_data("rooms", "room_id", info, "day_in", int(message.text))
            setup_menu(message)
    except Exception as e:
        bot.send_message(message.from_user.id, "Введено не число: {}".format(e))

def set_mon(message):
    try:
        if type(int(message.text)) == int:
            info = str(DBP.get_data("accounts", "room_current", "user_id", message.from_user.id)[0])
            bot.send_message(message.from_user.id, "Execute test: {}\n{}".format(message.from_user.id ,info))
            DBP.update_data("rooms", "room_id", info, "mon_in", int(message.text))
            setup_menu(message)
    except Exception as e:
        bot.send_message(message.from_user.id, "Введено не число: {}".format(e))

def set_pass(message):
    global password
    try:
        password = message.text
        setup_menu(message)
    except:
        bot.send_message(message.from_user.id, "Щось не так")

def set_room(message):
    try:
        room = int(message.text.split("#")[0])
        password = message.text.split("#")[1]
        if room == room_home:
            DBP.update_data("accounts", "user_id", message.from_user.id, "room_current", room)
        elif rooms.get(room) == password:
            DBP.update_data("accounts", "user_id", message.from_user.id, "room_current", room)
        else:
            bot.send_message(message.from_user.id, "Немає такої кімнати або пароль не вірний")
        bot.send_message(message.from_user.id, """
Денний +: {0}   
Змінити /change_day

Міячний +: {1}  
Змінити /change_mon

Активна кімната: {2}
Змінити /change_room

Домашня кімната: {3}
Змінити пароль /change_password
""".format(info[0], info[1], info[2], info[3]))
    except Exception as e:
        bot.send_message(message.from_user.id, e)

def mon_bal_handler(value):
    global mon_bal
    try:
        if type(int(value.text)) == int:
            mon_bal =int(mon_bal) - int(value.text)
            bot.send_message(value.from_user.id, "Місячний баланс {}".format(mon_bal))
    except Exception as e:
        bot.send_message(value.from_user.id, e)

def day_bal_handler(message):
    global day_bal
   
    day_bal = int(day_bal) - int(message.text)
    bot.send_message(message.from_user.id, "Денний баланс {}".format(day_bal))

def balance(message):
    keyboard = types.InlineKeyboardMarkup()

    key_mon_bal = types.InlineKeyboardButton(text='Місячна витрата', callback_data='mon_bal')  
    keyboard.add(key_mon_bal)

    balance = DBP.get_bal(message.from_user.id)
    bot.send_message(message.from_user.id, text='Денний: {0}\nМіячний баланс: {1}'.format(balance[0], balance[1]), reply_markup=keyboard)

def password_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choices(string.digits, k=size)), ''.join(random.choices(string.digits, k=size))


bot.polling(none_stop=True, interval = 0)




