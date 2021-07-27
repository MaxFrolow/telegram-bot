import telebot
import psycopg2
from psycopg2.extras import DictCursor
import bot_settings
from datetime import datetime

bot = telebot.TeleBot(bot_settings.telegram_bot_token)




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


@bot.message_handler(commands=['start', 'help'])
def help_menu(message):
    global location
    location = "menu"
    print(location)
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Баланс', 'Налаштувати Бота')
    bot.send_message(message.chat.id, 'Щоб налаштувати бота напиши /set \nЩо б почати користуватися напиши /bal\nАбо вибери з меню.',
                    reply_markup=keyboard)
    


@bot.message_handler(commands=['bal'])
def start_message(message):
    global location, location_sec
    print(location)
    location = 'menu'
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('День', 'Місяць')
    bot.send_message(message.chat.id, 'Вибери Баланс', reply_markup=keyboard)
    
    
@bot.message_handler(content_types=['text'])
def processing(message):
    global location, location_sec, day_bal, mon_bal, date_last, date_now, datem_last, datem_now
    print(location)
    print(datetime.now().day)
    date_now = datetime.now().day
    datem_now = datetime.now().month
    
    if date_last != datetime.now().day:
        date_last = datetime.now().day
        day_bal += day_in
    if datem_last != datetime.now().month:
        datem_last = datetime.now().month
        mon_bal += mon_in

   
    if message.text == 'Налаштувати Бота':
        print(location)
        location = 'set'
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('Змінити денний +', 'Змінити міячний +')
        bot.send_message(message.chat.id, 'Денний +: 200\nМісячний плюс:1000', reply_markup=keyboard)
    


    elif message.text == 'Баланс':
        print(location)
        location == 'bal'
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('День', 'Місяць')
        bot.send_message(message.chat.id, 'Вибери Баланс', reply_markup=keyboard)
    elif message.text in ('День', 'Місяць'):
        if message.text == 'День':
            print(location)
            location = 'day'
            bot.send_message(message.chat.id, 'Денний Баланс: {0}'.format(day_bal))
        else:
            print(location)
            location = 'mon'
            bot.send_message(message.chat.id, 'Місячний Баланс: {0}'.format(mon_bal))
    elif location in ('day','mon'):
        try:
            if location == 'day':
                print(location)
                day_bal = day_bal - int(message.text.lower())
                print(message)
                bot.send_message("678837081", 'Денний Баланс: {0}'.format(day_bal))
                bot.send_message(message.chat.id, 'Денний Баланс: {0}'.format(day_bal))
            else:
                print(location)
                mon_bal = mon_bal - int(message.text.lower())
                bot.send_message(message.chat.id, 'Місячний Баланс: {0}'.format(mon_bal))
        except:
            print(location)
            bot.send_message(message.chat.id, "Щось десь не туди введено.")
    
    else:
        try:
            isinstance(int(message.text), int) == True
            bot.send_message(message.chat.id, "Треба вибрати денний або місячний баланс.")
        except:
            print("last")
            bot.send_message(message.chat.id, "Щось десь не туди введено.")
        
           




bot.polling(none_stop=True, interval = 0)




