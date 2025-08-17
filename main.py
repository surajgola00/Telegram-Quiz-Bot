import random
import telebot
from telebot import types
from datetime import datetime
from flask import Flask, request
import mysql.connector
import io
import json
import botmessages as messages
from details import TOKEN, admin_id, secret, url, config
from database import db

bot = telebot.TeleBot(token=TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=url)
app = Flask(__name__)

@app.route('/'+secret, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

class bot_messages():
    @staticmethod
    def send_logs(msg):
        log = db.get_logs()
        if log is None:
            bot.send_message(msg.chat.id, 'some error occured ')
        bot.send_message(msg.chat.id, 'Here is the log: ')
        for dic in log:
            bot.send_message(msg.chat.id, f"{dic['location']} - {dic['error_message']} - {dic['timestamp']}")

    @staticmethod
    def contact_message(message):
        def send_to_admin(message):
            if message.text == '/cancel':
                bot.send_message(message.chat.id, 'Aborted\nFeel free to share your problem later.')
                return
            bot.forward_message(admin_id, message.chat.id, message.id)
            bot.send_message(message.chat.id, "Sent They' ll assist you in a while.")

        bot.reply_to(message, "We' re here to help! \nIf you have any questions or need assistance, you can reach out to us anytime. \nWe're just a message away. 📩")
        msg = bot.send_message(message.chat.id, "Send your problem I' ll forward to our developers team:\n/cancel to cancel the operation...")
        bot.register_next_step_handler(msg, callback=send_to_admin)

    @staticmethod
    def send_list(message):
        list = '/start\n/help\n/categories\n/users\n/contact\n/help\n/list\n/log\n/clear\n/dbcommand'
        list2= """
Here are the commands you can use:

/start: Kick off your quiz experience.
/help: Get assistance with commands and features.
/categories: View and choose quiz categories.
/contact: Reach out for support.
/list: View all commands.
Enjoy quizzing!"""

        if message.chat.id == admin_id:
            bot.reply_to(message, list)
            return
        bot.reply_to(message, list2)

    @staticmethod
    def send_users(message):
        data = db.get_user_data()
        if data is None:
            bot.send_message(message.chat.id, 'Some error occurred please try again later.')
        markup = types.InlineKeyboardMarkup(row_width=1)
        for dic in data:
            button = types.InlineKeyboardButton(f"{dic['name']}: {dic['user_name']}", callback_data=f"message-{dic['name']}-{dic['tg_id']}")
            markup.add(button)
        bot.send_message(message.chat.id, 'Here are the list of users connected:', reply_markup=markup)

    @staticmethod
    def edit_message(msg, text, markup=None):
        try:
            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.id, text=text, reply_markup=markup)
        except Exception:
            pass

    @staticmethod
    def send_category(message):
        categories = db.get_categories()
        if not categories:
            bot.send_message(message.chat.id, "No categories available at the moment. Please try again later.")
            return

        keyboard = types.InlineKeyboardMarkup()
        for category in categories:
            keyboard.add(types.InlineKeyboardButton(text=' '.join(category.split('_')).capitalize(), callback_data=f"selected_category-{category}"))

        keyboard.add(types.InlineKeyboardButton('❌', callback_data=f'delete'))
        bot.send_message(message.chat.id, "Choose a category that interests you and start answering questions! \n🧠 Each category has a set of questions to challenge your knowledge.\n\n Select a category to begin!", reply_markup=keyboard)

    @staticmethod
    def help_message(message):
        msg = """
Need help? \nYou've come to the right place! \n🛠️ Here are the commands you can use:\n\n
/start: Begin your quiz journey.
/categories: Browse through different quiz categories.
/list: View all available commands.
/contact: Get in touch with our support team.
If you have any questions, feel free to ask!"""
        bot.send_message(message.chat.id, msg)

    @staticmethod
    def send_welcome(message):
        current_time = datetime.now().time()  # Get the current time
        if current_time < datetime.strptime('12:00:00', '%H:%M:%S').time():  # Before noon
            greet = 'Good morning'
        elif current_time < datetime.strptime('16:00:00', '%H:%M:%S').time():  # Before 4 PM
            greet =  'Good afternoon'
        else:
            greet = 'Good evening'
        bot.reply_to(message, f"{greet} {message.from_user.first_name},\nHello and welcome to Quizzi Bot! \n🎉 Test your knowledge with our fun quizzes across various categories. Type /categories to explore our quiz topics and start playing. Let's get quizzing!")

db_connection = None

def get_db_connection():
    global db_connection
    try:
        if db_connection is None or not db_connection.is_connected():
            db_connection = mysql.connector.connect(**config)
        return db_connection
    except mysql.connector.Error as e:
        db.log_error(str(e), 'Database Connection')
        return None

#commands..........................................................................................................
@bot.message_handler(func=lambda message: True)
def check_command(message):
    db.initialise_user(message)
    if message.text == '/start':
        bot_messages.send_welcome(message)
    elif message.text =='/categories':
        bot_messages.send_category(message)
    elif message.text == '/users' and message.chat.id == admin_id:
        bot_messages.send_users(message)
    elif message.text == '/list':
        bot_messages.send_list(message)
    elif message.text == '/help':
        bot_messages.help_message(message)
    elif message.text == '/contact':
        bot_messages.contact_message(message)
    elif message.text == '/clear':
        db.delete_log(message)
    elif message.text == '/log' and message.chat.id == admin_id:
        db.send_log(message)
    else:
        return

@bot.message_handler(content_types=['document'])
def handle_file(message):
    if message.chat.id != admin_id:
        return

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        json_file = io.StringIO(downloaded_file.decode('utf-8'))
        questions = json.load(json_file)
        for dic in questions:
            if db.check_ques_presence(dic['category'], dic['q']):
                continue
            db.insert_data(dic)
        bot.send_message(message.chat.id, "Questions have been added to the database.")
    except Exception as e:
        db.log_error(str(e), 'handle_file')
        bot.send_message(message.chat.id, "An error occurred while handling the file.")




# calls....................................................................................................
@bot.callback_query_handler(func=lambda call: call.data.startswith('message'))
def ask_message(call):
    name, id = call.data.split('-')[1], call.data.split('-')[2]
    bot.answer_callback_query(call.id, f'user selected: {name}')
    msg = bot.send_message(call.message.chat.id, f'send your message for {name} or /cancle to abort:')

    def send_to_user(message, data):
        if message.text == '/cancle':
            bot.send_message(message.chat.id, 'aborted!')
            return

        bot.send_message(data[1], message.text)
        bot.send_message(message.chat.id, f'Sent successfully to {data[0]}')

    bot.register_next_step_handler(message=msg, callback=lambda message: send_to_user(message, (name, id)))

@bot.callback_query_handler(func=lambda call: call.data.startswith('selected_category'))
def send_question(call):
    category = call.data.split('-')[1]
    question_no = db.get_user_score(call.from_user.id, category)
    if question_no is None:
        bot_messages.edit_message(call.message, 'Sorry an error occurred please try again later')
    total_q = db.get_total_no_q(category)

    if question_no > total_q:
        bot_messages.edit_message(call.message, text=f"WOW!\nYou 've reched the end of the questions list of {category} category\n explore other categories /categories till we update our database.")
        bot.send_message(admin_id, f'Alert User \n{call.from_user.first_name} with id @{call.from_user.username}\n had completed the questions till end of {category} category.')
        return

    q_data = db.get_question(category, question_no)
    if q_data is None:
        bot.send_message(call.message.chat.id, 'Some error occurred please try again later.')
    markup = types.InlineKeyboardMarkup(row_width=2)
    options = q_data['options'].split(',')
    for option in options:
        button = types.InlineKeyboardButton(option, callback_data=f'answer-{q_data["ans"]}-{option}-{category}-{q_data["q_no"]}')
        markup.add(button)
    del_button = types.InlineKeyboardButton('❌', callback_data=f'delete')
    help_button = types.InlineKeyboardButton('Hint❗', callback_data=f'hint-{category}-{q_data["q_no"]}')
    report = types.InlineKeyboardButton('Report🛑', callback_data=f'report-{category}-{q_data["q_no"]}')
    skip_button = types.InlineKeyboardButton('Skip▶', callback_data=f'skip-{category}-{q_data["q_no"]}')
    markup.add(report, del_button)
    markup.add(skip_button, help_button)

    bot_messages.edit_message(call.message, f"Q{q_data['q_no']}:\n {q_data['q']}", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('answer'))
def check_answer(call):
    try:
        ans, selected, category, q_no = call.data.split('-')[1], call.data.split('-')[2], call.data.split('-')[3], int(call.data.split('-')[4])
        q_dic = db.get_question(category, q_no)
        if q_dic is None:
            bot.send_message(call.message.chat.id, 'Some error occurred please try again later.')
        if ans == selected:
            db.update_score(call.message.chat.id, category, q_no+1)
            bot.answer_callback_query(call.id, random.choice(messages.correct_ans))
            markup = types.InlineKeyboardMarkup()
            del_button = types.InlineKeyboardButton('❌', callback_data=f'delete')
            next_button = types.InlineKeyboardButton('Next▶', callback_data=f'selected_category-{category}-{q_dic["q_no"]+1}')
            markup.add(del_button, next_button)
            bot_messages.edit_message(call.message, text=f"Correct🎉\n\nDid You Know\n{q_dic['info']}", markup=markup)
        else:
            bot.answer_callback_query(call.id, random.choice(messages.wrong_ans))
    except Exception as e:
        db.log_error(str(e), 'check_answer')

@bot.callback_query_handler(func=lambda call: call.data.startswith('skip'))
def skip_question(call):
    q_type, q_no = call.data.split('-')[1], int(call.data.split('-')[2])
    db.update_score(call.message.chat.id, q_type, q_no+1)
    send_question(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('report'))
def report_question(call):
    q_type, q_no = call.data.split('-')[1], int(call.data.split('-')[2])
    q_dic = db.get_question(q_type, q_no)
    if q_dic is None:
        bot.send_message(call.messafe.chat.id, 'Some error occurred please try again later.')
    bot.send_message(admin_id, f"Question Reported‼\n by the user {call.message.chat.first_name} id {call.from_user.id} {call.message.from_user.username}\n Question:\n{q_dic['q']}\nOptions:\n{q_dic['options']}\nAnswer:\n{q_dic['ans']}")
    bot.answer_callback_query(call.id, 'Question Reported‼')
    bot.send_message(call.message.chat.id, 'Question Reported!!!\nOur admins are on the way...')
    skip_question(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('hint'))
def get_hint(call):
    q_type, q_no = call.data.split('-')[1], int(call.data.split('-')[2])
    q_dic = db.get_question(q_type, q_no)
    if q_dic is None:
        bot.send_message(call.messafe.chat.id, 'Some error occurred please try again later.')
    if q_dic['hint'] not in call.message.text:
        bot_messages.edit_message(call.message, text=f"{call.message.text}\n\nHint:\n{q_dic['hint']}", markup=call.message.reply_markup)

@bot.callback_query_handler(func=lambda call: call.data == 'delete')
def delete_message(call):
    try:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    except Exception:
        bot.answer_callback_query(callback_query_id=call.id, text='Unable to delete message!')