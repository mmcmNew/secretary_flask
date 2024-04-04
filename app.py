import glob
import os
import json
import re
from datetime import datetime

import sqlite3
import random

from flask import Flask, render_template, jsonify, request

from modules.geminiVPN import gemini_proxy_response
from utilites import find_target_module, save_to_base, save_to_base_modules, find_info, generate_cards
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
    audio_path = tts(text)  # Генерируем аудио из текста
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


@app.route('/memory', methods=['POST'])
def memory():
    data = request.json
    request_type = data.get('type', None)
    params = data.get('params', None)
    if request_type == 'words':
        new_cards = generate_cards(cards_type=request_type, string_words=params)
    elif request_type == 'check':
        pass
    else:
        count = int(params.get('count', 50))
        new_cards = generate_cards(count)

    if not new_cards:
        new_cards = generate_cards(50)
    return jsonify({'cards': new_cards})


@app.route('/check_results', methods=['POST'])
def check_results():
    data = request.json
    original_text = data.get('text', '')
    user_text = data.get('userText', '')

    # Удаление знаков препинания и приведение к нижнему регистру
    cleaned_original_text = re.sub(r'[^\w\s]', '', original_text).lower()
    cleaned_user_text = re.sub(r'[^\w\s]', '', user_text).lower()

    # Разделение строк на слова
    original_words = cleaned_original_text.split()
    user_words = cleaned_user_text.split()

    # Сравнение слов по позициям и выделение неправильных
    result_words = []
    correct_count = 0
    incorrect_count = 0
    for index, word in enumerate(user_words):
        if index < len(original_words) and word == original_words[index]:
            correct_count += 1
            result_words.append(word)
        else:
            incorrect_count += 1
            # Добавление HTML тега для выделения слова красным цветом
            result_words.append(f'<span style="color: red;">{word}</span>')

    # Подсчет общего результата
    total_words = len(original_words)
    correct_percentage = int((correct_count / total_words) * 100) if total_words else 0

    # Формирование строки с результатом
    result_text = ' '.join(result_words)
    final_result = f'Результат: {correct_percentage}% ({correct_count}/{total_words}). <br>{result_text}'

    return jsonify(final_result)


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
        target_module, module_type = find_target_module(text)
        print(f'new_message: target_module: {target_module}')
        match module_type:
            case 'component':
                div_time = datetime.now().strftime("%Y%m%d%H%M%S")
                random_id = random.randint(1000, 9999)
                component_info = find_info(target_module, text)
                component_info['id'] = f'{div_time}{random_id}'
                print(f'new_message: component_info: {component_info}')
                ai_answer = {'user_id': 2, 'text': f'Запускаю {target_module}'}
                context = {target_module: component_info}
                component_div = render_template(f'{target_module}.html', **context)
                message_type = 'component'
            case 'journal':
                command = {'target_module': target_module, 'text': text}
                if request.files:
                    command['files'] = request.files
                result = save_to_base_modules(command)  # обработчик для модулей которые сохраняют записи в базу
                ai_answer = {'user_id': 2, 'text': result['text']}
            case 'action_module':
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
        div_time = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = random.randint(1000, 9999)

        message['name'] = users[ai_answer['user_id']]['name']
        message['avatar'] = users[ai_answer['user_id']]['avatar']
        message['id'] = f'{div_time}{random_id}'

    chat_message = render_template('message_template.html', message=message)
    if message_type == 'component':
        return jsonify({'div': chat_message, 'component': {'div': component_div, 'id': component_info['id']},
                        'type': message_type})
    if message_type == 'action_module':
        return jsonify(
            {'div': chat_message, 'action_module_div': {'div': action_module['div'], 'id': action_module['id']},
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
