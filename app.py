import glob
import os
import json
import re
from datetime import datetime

import random

from flask import Flask, render_template, jsonify, request
from flask_admin import Admin
from models import *
from admin import MyModelView

from modules.geminiVPN import gemini_proxy_response
from utilites import find_target_module, save_to_base, save_to_base_modules, find_info, generate_cards
from text_to_edge_tts import tts

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///F:/Projects/Python/jinja2/secretary/new_base.db'
app.config['SECRET_KEY'] = 'my_secret'

# Инициализация SQLAlchemy с текущим приложением
db.init_app(app)

# Инициализация Flask-Admin
admin = Admin(app, name='Secretary', template_mode='bootstrap3')

with app.app_context():
    db.create_all()  # Создаём таблицы в базе данных
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(ChatHistory, db.session))
    admin.add_view(MyModelView(Diary, db.session))
    admin.add_view(MyModelView(ProjectJournal, db.session))
    admin.add_view(MyModelView(TradingJournal, db.session))
    admin.add_view(MyModelView(BacktestJournal, db.session))
    admin.add_view(MyModelView(Task, db.session))


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


@app.route('/users')
def list_users():
    users_list = User.query.all()
    users = [user.to_dict() for user in users_list]
    return jsonify(users)


@app.route('/')
def home():
    tabs = [
        {'id': 'nav-home', 'title': 'Home'},
        {'id': 'nav-profile', 'title': 'Profile'},
        {'id': 'nav-contact', 'title': 'Contact'},
        {'id': 'nav-disabled', 'title': 'Disabled'},
    ]

    commands = ['Запустить таймер','Запустить метроном', 'Запусти память', 'Фокусировка', 'Расслабление', 'Демонстрация']

    # Загрузка всех сообщений и связанных пользователей из базы данных
    messages = ChatHistory.query.join(ChatHistory.user).order_by(ChatHistory.message_id.desc()).limit(50).all()
    messages = messages[::-1]
    # Преобразование сообщений в формат, подходящий для передачи в шаблон
    messages_data = []
    for message in messages:
        if message.message_id is None:
            continue
        message_data = {
            'id': message.message_id,
            'user_id': message.user_id,
            'date': message.date.isoformat() if message.date else None,
            'time': message.time,
            'text': message.text,
            'image': message.image,
            'position': message.position,
            'name': message.user.user_name,
            'avatar': message.user.avatar_src,
        }
        messages_data.append(message_data)

    html_content = render_template('index.html', tabs=tabs, messages=messages_data, commands=commands)
    return html_content


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/memory', methods=['POST'])
def memory():
    data = request.json
    request_type = data.get('type', None)
    params = data.get('params', None)
    new_cards = {}
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
    delimiter = data.get('delimiter', ' ')

    # Удаление знаков препинания и приведение к нижнему регистру
    cleaned_original_text = original_text.lower()
    cleaned_user_text = user_text.lower()

    # Разделение строк на слова
    original_words = cleaned_original_text.split(delimiter)
    user_words = cleaned_user_text.split(',')

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
    component_div = ''
    component_info = None
    action_module = None
    # для первого запроса формируем вывод в чат
    if message_type == 'request':
        message = {'table_name': 'chat_history', 'user_id': 1, 'time': current_time, 'text': text, 'position': 'r'}
        result = save_to_base(message)
        print(result)
        message['name'] = 'Me'
        message['avatar'] = 'me.png'
    else:
        # при повторном запросе отправляем его секретарю
        users_list = User.query.all()
        users = [user.to_dict() for user in users_list]
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

        message = {'table_name': 'chat_history', 'user_id': ai_answer['user_id'],
                   'time': current_time, 'text': ai_answer['text'], 'position': 'l'}

        result = save_to_base(message)
        print(result)
        div_time = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = random.randint(1000, 9999)
        user_info = next((user for user in users if user['id'] == ai_answer['user_id']), None)
        if user_info:
            message['name'] = user_info['user_name']
            message['avatar'] = user_info['avatar_src']
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
