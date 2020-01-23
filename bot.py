import telebot
import psycopg2
from psycopg2.extras import DictCursor


bot = telebot.TeleBot()




location = 'menu'
name = ''
last_name = ''
birth_date = ''


@bot.message_handler(func=lambda message: True, content_types=['text'])
def get_message(message):
    global location, name, last_name, birth_date
    print(location)
    #go to main menu
    if message.text.lower() == "hi" or message.text.lower() == "menu" and location == 'menu':
        bot.send_message(message.from_user.id,
                         """
                         Hello, choose your action:
                             1)Registration
                             2)Deleting
                         """)

    #if we in menu and choose Registration, ask name
    elif message.text == "1" or message.text.lower() == "registration" or message.text.lower() == 'no':
        location = 'name'
        bot.send_message(message.from_user.id,
                         """
                         What is your name?
                         """)
        location = 'last_name'

    #if we write command '/help'
    elif message.text == "/help":
        bot.send_message(message.from_user.id,
                         """First write 'menu' to open the menu.
                            You can choose your action by writing number of action or writing name of action, like '1' or 'Registration.
                         """)
    # navigation
    else:
        #this registration way

        #we already take neme, so save name and go to last_name
        if location == 'last_name':
            name = message.text
            bot.send_message(message.from_user.id,
                             """
                             What is your last name?
                             """)
            location = 'birth_date'

        # we already take last name, so save last_name and go birth_day
        elif location == 'birth_date':
            last_name = message.text
            bot.send_message(message.from_user.id,
                             """
                             What is your birth date?(DD.MM.YYYY)
                             """)
            location = 'accepting'

        # we alreade take birth_date, so save it and confirm all data
        elif location == 'accepting':
            birth_date = message.text.lower()
            bot.send_message(message.from_user.id,
                             "So, confirm your data:\nYou are " + name + ' ' + last_name + " and birth " + str(
                                 birth_date) + "\nSend 'Yes' if all right and 'No' if you want change your data.\nIf you want refuse send 'Quit' ")
            location = 'save_or_not'

        #answer to confirmation
        elif location == 'save_or_not':
            if message.text.lower() == 'yes':
                bot.send_message(message.from_user.id, 'Saving data, wait please.')

            # enter data again
            elif message.text.lower() == 'no':
                name, last_name, birth_date = '', '', ''
                name(message)
            # not save and go to meny
            elif message.text.lower() == 'quit':
                name, last_name, birth_date = '', '', ''
                location = 'menu'


bot.polling(none_stop=True, interval = 0)




