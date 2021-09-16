import telebot
import psycopg2
from psycopg2.extras import DictCursor
import bot_settings
from datetime import datetime
from db_process import DbProcessor
from telebot import types
import random

#--------------------------------------------------------
# Main Processors
#-------------------------------------------------------
bot = telebot.TeleBot(bot_settings.telegram_bot_token)
DBP = DbProcessor


#--------------------------------------------------------
# Test vars
#-------------------------------------------------------
location = 'menu'
location_sec = 'index'
day_bal = 0
mon_bal = 0
day_in = 200
mon_in = 1000
date_last = ""
date_now = ""
datem_last = ""
datem_now = ""


#--------------------------------------------------------
# Messages handling
#-------------------------------------------------------

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # Если написали «Привет»
    try:
        if message.text in ["/help", "/start"]:
            
            keyboard = types.InlineKeyboardMarkup()

            key_bal = types.InlineKeyboardButton(text='Баланс', callback_data='balance') 
            keyboard.add(key_bal)

            key_setup = types.InlineKeyboardButton(text='Setup', callback_data='setup') 
            keyboard.add(key_setup)

            bot.send_message(message.from_user.id, text='Привіт, чим можу допомогти?', reply_markup=keyboard)
        elif message.text == "/setup":
            setup_menu(message)
        
        elif message.text == "/change_day":
            sent = bot.send_message(message.chat.id, 'Вкажи новий денний приріст')
            bot.register_next_step_handler(sent, set_day)
        
        elif message.text == "/change_mon":
            sent = bot.send_message(message.chat.id, 'Вкажи новий місячний приріст')
            bot.register_next_step_handler(sent, set_mon)
        
        elif message.text == "/change_room":
            bot.send_message(message.from_user.id, "Ще не імплементовано")
        elif type(int(message.text)) == int:
            day_bal_handler(message)
        else:
            bot.send_message(message.from_user.id, "Я тебя не розумію. Напиши /help.")
    except Exception as e:
        bot.send_message(message.from_user.id, e)

#--------------------------------------------------------
#Callback
#-------------------------------------------------------

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "setup": 
        bot.send_message(call.message.chat.id, """
Денний +: {0}   
Змінити /change_day

Міячний +: {1}  
Змінити /change_mon

Активна кімната: 3523343
Змінити /change_room

Домашня кімната: 1223534 
""".format(day_in, mon_in))
    elif call.data == "balance":
        keyboard = types.InlineKeyboardMarkup()

        key_mon_bal = types.InlineKeyboardButton(text='Місячна витрата', callback_data='mon_bal')  
        keyboard.add(key_mon_bal)

        bot.send_message(call.message.chat.id, text='Денний: {0}\nМіячний баланс: {1}'.format(day_bal, mon_bal), reply_markup=keyboard)

    elif call.data == "mon_bal":
        sent = sent = bot.send_message(call.message.chat.id, 'Вкажи витрату з місячного балансу')
        bot.register_next_step_handler(sent, mon_bal_handler)




#--------------------------------------------------------
#Main functions
#-------------------------------------------------------
def setup_menu(message_type):
    global day_in, mon_in
    bot.send_message(message_type.chat.id, """
Денний +: {0}   
Змінити /change_day

Міячний +: {1}  
Змінити /change_mon

Активна кімната: 3523343
Змінити /change_room

Домашня кімната: 1223534 
""".format(day_in, mon_in))
def set_day(message):
    global day_in
    try:
        if type(int(message.text)) == int:
            day_in = message.text
            setup_menu(message)
    except:
        bot.send_message(message.from_user.id, "Введено не число")

def set_mon(message):
    global mon_in
    try:
        if type(int(message.text)) == int:
            mon_in = message.text
            setup_menu(message)
    except:
        bot.send_message(message.from_user.id, "Введено не число")

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


bot.polling(none_stop=True, interval = 0)




