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



help_text ="""
Спочатку потрібно налаштувати бота: /setup

Налаштування:
Показані дані для твоєї кімнати.
Для того що б долучитися до іншої кімнати, спитай домашню кімнату власника і пароль.
Далі: /change_room і слідувати інструкціям.

Використання:
Будь яке число буде відніматися від денного балансу.
Для відняття від місячного балансу використати: 
/mon_bal
або
/start -> Баланс -> Місячна витрата
"""
#--------------------------------------------------------
# Messages handling
#-------------------------------------------------------

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # Если написали «Привет»
    
    try:
        currentDay = int(datetime.now().strftime('%d'))
        currentMonth = int(datetime.now().strftime('%m'))
        data = DBP.get_room_data(message.chat.id, "room_day_in, room_mon_in, day_bal, mon_bal, day_in, mon_in, room_id")
        if currentDay != data[0]:
            summ = int(data[4]) + int(data[2]) 
            DBP.update_date_data("rooms", "room_id", data[6], "(day_bal, room_day_in)", "('{}', '{}')".format( summ, currentDay))
        if currentMonth != data[1]:
            summ = int(data[5]) + int(data[3]) 
            DBP.update_date_data("rooms", "room_id", data[6], "(mon_bal, room_mon_in)", "('{}', '{}')".format(summ , currentMonth))
        
    except:
        print('empty')
    try:
    
        if message.text == "/help":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('/start', 'Перевірити Баланс', '/setup', "/mon_bal")
            bot.send_message(message.from_user.id, text='Завантажено базові команди', reply_markup=markup)
            bot.send_message(message.from_user.id, text=help_text)
        
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
        bot.send_message(message.from_user.id, "Введено не число")

#--------------------------------------------------------
#Callback
#-------------------------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "setup": 
        try:
            info = DBP.get_room_data(call.message.chat.id, "day_in, mon_in, room_current, room_home")
            if not info:
                password, room_id = password_generator()
                currentDay = datetime.now().strftime('%d')
                currentMonth = datetime.now().strftime('%m')
                DBP.save_data("rooms", 
                            "room_id, day_in, mon_in, day_bal, mon_bal, room_day_in, room_mon_in, password",
                            "{}, 300, 3000, 300, 3000, {}, {}, {}".format(room_id, currentDay, currentMonth, password))
                DBP.save_data("accounts", "user_id, room_current, room_home", "{}, {}, {}".format(call.message.chat.id, room_id, room_id))
            info = DBP.get_room_data(call.message.chat.id, "day_in, mon_in, room_current, room_home")
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
        balance = DBP.get_room_data(call.message.chat.id, "day_bal, mon_bal")
        bot.send_message(call.message.chat.id, text='Денний: {0}\nМіячний баланс: {1}'.format(balance[0], balance[1]), reply_markup=keyboard)

    elif call.data == "mon_bal":
        sent = sent = bot.send_message(call.message.chat.id, 'Вкажи витрату з місячного балансу')
        bot.register_next_step_handler(sent, mon_bal_handler)




#--------------------------------------------------------
#Main functions
#-------------------------------------------------------
def setup_menu(message_type):
    try:
        info = DBP.get_room_data(message_type.chat.id, "day_in, mon_in, room_current, room_home")
        if not info:
            password, room_id = password_generator()
            currentDay = datetime.now().strftime('%d')
            currentMonth = datetime.now().strftime('%m')
            DBP.save_data("rooms", 
                          "room_id, day_in, mon_in, day_bal, mon_bal, room_day_in, room_mon_in, password",
                          "{}, 300, 3000, 300, 3000, {}, {}, {}".format(room_id, currentDay, currentMonth, password))
            DBP.save_data("accounts", "user_id, room_current, room_home", "{}, {}, {}".format(message_type.chat.id, room_id, room_id))
        info = DBP.get_room_data(message_type.chat.id, "day_in, mon_in, room_current, room_home")
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
            info = str(DBP.get_data("accounts", "room_home", "user_id", message.from_user.id)[0])
            DBP.update_data("rooms", "room_id", info, "day_in", int(message.text))
            setup_menu(message)
    except Exception as e:
        bot.send_message(message.from_user.id, "Введено не число: {}".format(e))

def set_mon(message):
    try:
        if type(int(message.text)) == int:
            info = str(DBP.get_data("accounts", "room_home", "user_id", message.from_user.id)[0])
            DBP.update_data("rooms", "room_id", info, "mon_in", int(message.text))
            setup_menu(message)
    except Exception as e:
        bot.send_message(message.from_user.id, "Введено не число: {}".format(e))

def set_pass(message):
    data = DBP.get_home_data(message.from_user.id, "room_id")
    try:
        DBP.update_data( "rooms", "room_id", data[0], "password", message.text)
        bot.send_message(message.from_user.id, "Змінено" )
        setup_menu(message)
    except:
        bot.send_message(message.from_user.id, "Щось не так" )


def set_room(message):
    try:
        room = int(message.text.split("#")[0])
        password = message.text.split("#")[1]
        data = DBP.get_room_set(room, "password")
        if password == data[0]:
            DBP.update_data("accounts", "user_id", message.from_user.id, "room_current", room)
        else:
            bot.send_message(message.from_user.id, "Немає такої кімнати або пароль не вірний")
        info = DBP.get_room_data(message.from_user.id, "day_in, mon_in, room_current, room_home")
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

def mon_bal_handler(message):
    try:
        data = DBP.get_room_data(message.from_user.id, "mon_bal, room_id")
        mon_bal = int(data[0]) - int(message.text)
        DBP.update_data("rooms", "room_id", data[1], "mon_bal", mon_bal)

        mon_bal = DBP.get_room_data(message.from_user.id, "mon_bal")
        bot.send_message(message.from_user.id, "Місячний баланс {}".format(mon_bal[0]))
    except:
        bot.send_message(message.from_user.id, "Щось пішло не так ")

def day_bal_handler(message):
    try:
        data = DBP.get_room_data(message.from_user.id, "day_bal, room_id")
        day_bal = int(data[0]) - int(message.text)
        DBP.update_data("rooms", "room_id", data[1], "day_bal", day_bal)

        day_bal = DBP.get_room_data(message.from_user.id, "day_bal")
        bot.send_message(message.from_user.id, "Денний баланс {}".format(day_bal[0]))
    except:
        bot.send_message(message.from_user.id, "Щось пішло не так ")

def balance(message):
    keyboard = types.InlineKeyboardMarkup()

    key_mon_bal = types.InlineKeyboardButton(text='Місячна витрата', callback_data='mon_bal')  
    keyboard.add(key_mon_bal)

    balance = DBP.get_room_data(message.from_user.id, "day_bal, mon_bal")
    bot.send_message(message.from_user.id, text='Денний: {0}\nМіячний баланс: {1}'.format(balance[0], balance[1]), reply_markup=keyboard)

def password_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choices(string.digits, k=size)), ''.join(random.choices(string.digits, k=size))

try:
    bot.polling(none_stop=True)
except Exception as err:
    logging.error(err)
    time.sleep(5)
    print ("Internet error!")




