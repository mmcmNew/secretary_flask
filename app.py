import glob
import os
from datetime import datetime

import sqlite3
from flask import Flask, render_template, jsonify, request

from utilites import process_command, save_to_base
from text_to_edge_tts import tts

app = Flask(__name__)


@app.route('/generate-tts', methods=['POST'])
def generate_tts():
    save_path = os.path.join(os.path.dirname(__file__), 'static', 'temp')
    # Поиск файлов, которые начинаются с 'edge_audio_' и заканчиваются на '.mp3'
    for file_path in glob.glob(os.path.join(save_path, 'edge_audio_*.mp3')):
        try:
            os.remove(file_path)
            print(f'Файл {file_path} был успешно удален')
        except OSError as e:
            print(f'Ошибка при удалении файла {file_path}: {e}')
    text = request.form['text']
    audio_path = tts(text) # Генерируем аудио из текста
    return jsonify(audioUrl=audio_path)


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
    print(f'new_message: Список файлов: {request.files}')
    # для первого запроса формируем вывод в чат
    if message_type == 'request':
        message = {'table_name': 'ChatHistory', 'user_id': 1, 'time': current_time, 'text': text, 'position': 'r'}
        result = save_to_base(message)
        print(result)
        message['name'] = 'Me'
        message['avatar'] = 'me.png'
    else:
        # при повторном запросе отправляем его секретарю
        users = get_users()
        command = {'text': text}
        if request.files:
            command['files'] = request.files
        ai_answer = process_command(command) or {'user_id': 2, 'text': 'Уточните запрос'}
        message = {'table_name': 'ChatHistory', 'user_id': ai_answer['user_id'],
                   'time': current_time, 'text': ai_answer['text'], 'position': 'l'}

        result = save_to_base(message)
        print(result)
        message['name'] = users[ai_answer['user_id']]['name']
        message['avatar'] = users[ai_answer['user_id']]['avatar']

    chat_message = render_template('message_template.html', message=message)

    return jsonify({'div': chat_message, 'type': message_type})


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0')
