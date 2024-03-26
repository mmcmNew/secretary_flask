from datetime import datetime

import sqlite3
from flask import Flask, render_template, jsonify, request

from utilites import process_command, save_to_base

app = Flask(__name__)


@app.route('/tables')
def list_tables():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tables = [row[0] for row in cursor.fetchall()]
    connection.close()
    return jsonify(list(tables))


def get_users():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users')
    users = {}
    for row in cursor.fetchall():
        user_data = {'name': row[1],
                     'avatar': row[2]}
        users[row[0]] = user_data
    connection.close()
    return users


@app.route('/')
def home():
    connection = sqlite3.connect('database.db')
    tabs = [
        {'id': 'nav-home', 'title': 'Home'},
        {'id': 'nav-profile', 'title': 'Profile'},
        {'id': 'nav-contact', 'title': 'Contact'},
        {'id': 'nav-disabled', 'title': 'Disabled'}
    ]

    commands = [
        {'name': 'Запустить таймер', 'command': 'timer start'},
        {'name': 'Запустить метроном', 'command': 'timer metronome'}
    ]

    cursor = connection.cursor()
    users = get_users()
    cursor.execute('SELECT * FROM ChatHistory')
    messages = []
    for row in cursor.fetchall():
        if row[0] is None:
            continue
        message_data = {'id': row[0],
                        'user_id': row[1],
                        'date': row[2],
                        'time': row[3],
                        'text': row[4],
                        'image': row[5],
                        'position': row[6]}

        message_data['name'] = users[message_data['user_id']]['name']
        message_data['avatar'] = users[message_data['user_id']]['avatar']

        messages.append(message_data)
    connection.close()
    html_content = render_template('index.html', tabs=tabs, messages=messages, commands=commands)
    return html_content


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/new-message', methods=['POST'])
def new_message():
    current_time = datetime.now().strftime("%H:%M")
    text = request.form.get('message')
    message_type = request.form.get('type')
    print(f'message_type: "{message_type}"')
    # print(text)
    # если это запрос от пользователя, то формируем вывод в чат
    if message_type == 'request':
        message = {'table_name': 'ChatHistory', 'user_id': 1, 'time': current_time, 'text': text, 'position': 'r'}
        result, error = save_to_base(message)
        if not result:
            print(error)
        message['name'] = 'Me'
        message['avatar'] = 'me.png'
    else:
        # если это запрос на ответ секретаря получаем ответ секретаря
        users = get_users()
        ai_answer = process_command(text) or {'user_id': 2, 'text': 'Уточните запрос'}
        message = {'table_name': 'ChatHistory', 'user_id': ai_answer['user_id'],
                   'time': current_time, 'text': ai_answer['text'], 'position': 'l'}

        result, error = save_to_base(message)
        if not result:
            print(error)
        message['name'] = users[ai_answer['user_id']]['name']
        message['avatar'] = users[ai_answer['user_id']]['avatar']

    chat_message = render_template('message_template.html', message=message)

    return jsonify({'div': chat_message, 'type': message_type})


if __name__ == '__main__':
    app.run(debug=True)
