import glob
import os
import json
from datetime import datetime

import sqlite3
import random

from flask import Flask, render_template, jsonify, request

from modules.geminiVPN import gemini_proxy_response
from utilites import find_target_module, save_to_base, save_to_base_modules, find_info, parse_time
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
        message_data = {'id': row[0], 'user_id': row[1], 'date': row[2], 'time': row[3], 'text': row[4],
                        'image': row[5], 'position': row[6]}

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
    tool_panel_div = None
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
        target_module = find_target_module(text)
        print(f'new_message: target_module: {target_module}')
        match target_module:
            case 'timer':
                div_time = datetime.now().strftime("%Y%m%d%H%M%S")
                random_id = random.randint(1000, 9999)
                timer_info = {'time': parse_time(text), 'info': find_info('timer', text),
                              'id': f'{div_time}{random_id}'}
                ai_answer = {'user_id': 2, 'text': f'Запускаю таймер '}
                timer_div = render_template('timer.html', timer=timer_info)
                message_type = 'timer'
            case 'metronome':
                div_time = datetime.now().strftime("%Y%m%d%H%M%S")
                random_id = random.randint(1000, 9999)
                metronome_info = {'info': find_info('metronome', text),
                                  'id': f'{div_time}{random_id}'}
                print(f'new_message: metronome_info: {metronome_info}')
                ai_answer = {'user_id': 2, 'text': f'Запускаю метроном. bpm {metronome_info['info']['bpm']} '}
                metronome_div = render_template('metronome.html', metronome=metronome_info)
                message_type = 'metronome'
            case 'trading_journal' | 'diary' | 'project_journal':
                command = {'target_module': target_module, 'text': text}
                if request.files:
                    command['files'] = request.files
                result = save_to_base_modules(command) # обработчик для модулей которые сохраняют записи в базу
                ai_answer = {'user_id': 2, 'text': result['text']}
            case 'productivity':
                action_module = action_module_processing(target_module)
                if action_module:
                    message_type = 'action_module'
                    ai_answer = {'user_id': 2, 'text': f'Запускаю модуль {target_module}'}
                else:
                    ai_answer = {'user_id': 2, 'text': 'Проблемы при запуске модуля'}
            case 'ai_chat':
                # Если целевой модуль ai передаем всю команду
                gemini_answer = gemini_proxy_response(text)
                ai_answer = {'user_id': 3, 'text': gemini_answer}
            case _:
                ai_answer = {'user_id': 2, 'text': 'Уточните запрос'}

        message = {'table_name': 'ChatHistory', 'user_id': ai_answer['user_id'],
                   'time': current_time, 'text': ai_answer['text'], 'position': 'l'}

        result = save_to_base(message)
        print(result)
        message['name'] = users[ai_answer['user_id']]['name']
        message['avatar'] = users[ai_answer['user_id']]['avatar']

    chat_message = render_template('message_template.html', message=message)
    if message_type == 'timer':
        return jsonify({'div': chat_message, 'timer_div': {'div': timer_div, 'id': timer_info['id']},
                        'type': message_type})
    if message_type == 'metronome':
        return jsonify({'div': chat_message, 'metronome_div': {'div': metronome_div, 'id': metronome_info['id']},
                        'type': message_type})
    if message_type == 'action_module':
        return jsonify({'div': chat_message, 'action_module_div': {'div': action_module['div'], 'id': action_module['id']},
                        'type': message_type})
    return jsonify({'div': chat_message, 'type': message_type})


def action_module_processing(module_name):
    module_path = os.path.join('modules', f'{module_name}.json')
    print(f'action_module_processing: module_path: {module_path}')
    try:
        with open(module_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        print(f'action_module_processing: {e}')
        return None

    print(f'action_module_processing: data: {data}')

    div_time = datetime.now().strftime("%Y%m%d%H%M%S")
    random_id = random.randint(1000, 9999)
    action_module_id = f'{div_time}{random_id}'
    for step in data['steps']:
        for action in step['actions']:
            random_id = random.randint(1000, 9999)
            action['id'] = f'{action_module_id}-{random_id}'
        random_id = random.randint(1000, 9999)
        step['id'] = f'{action_module_id}-{random_id}'
    action_module = {'id': action_module_id, 'name': data['name'], 'steps': data['steps']}
    action_module_div = render_template('action_module.html', action_module=action_module)

    return {'id': action_module_id, 'div': action_module_div}


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0')
