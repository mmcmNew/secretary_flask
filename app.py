import glob
import os
import json

from datetime import datetime

import random

from flask import Flask, render_template, jsonify, request
from flask_admin import Admin
from models import *
from admin import MyModelView
from sqlalchemy import or_

from modules.geminiVPN import gemini_proxy_response
from utilites import find_target_module, save_to_base, save_to_base_modules, find_info, generate_cards
from text_to_edge_tts import tts

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///F:/Projects/Python/jinja2/secretary/new_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my_secret'

# Инициализация SQLAlchemy с текущим приложением
db.init_app(app)

# Инициализация Flask-Admin
admin = Admin(app, name='Secretary', template_mode='bootstrap4')

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
        {'id': 'nav-ToDo', 'title': 'ToDo'},
        {'id': 'nav-contact', 'title': 'Contact'},
        {'id': 'nav-disabled', 'title': 'Disabled'},
    ]

    commands = ['Запустить таймер', 'Запустить метроном', 'Запусти память', 'Фокусировка', 'Расслабление',
                'Демонстрация']

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
            'image': message.files,
            'position': message.position,
            'name': message.user.user_name,
            'avatar': message.user.avatar_src,
        }
        messages_data.append(message_data)

    html_content = render_template('index.html', tabs=tabs, messages=messages_data, commands=commands,
                                   to_do_groups=list_groups())
    return html_content


def list_groups():
    # Получаем все группы
    tasks_groups = Group.query.all()

    # Получаем списки, которые не принадлежат ни к одной группе
    ungrouped_lists = List.query.filter(~List.groups.any()).all()

    # Преобразуем данные в список словарей для передачи в шаблон
    group_data = []
    for group in tasks_groups:
        group_data.append({
            'group_id': group.id,
            'group_name': group.name,
            # Для каждого списка подсчитываем количество задач
            'lists': [
                {'id': f'{lst.id}_{group.id}_list', 'name': lst.name, 'task_count': len(lst.tasks)}
                for lst in group.lists
            ]
        })

    # Также подсчитываем задачи для негруппированных списков
    ungrouped_data = [
        {'id': f'{lst.id}_list', 'name': lst.name, 'task_count': len(lst.tasks)}
        for lst in ungrouped_lists
    ]

    # подсчет количества tusks не входящих ни в одну группу
    tasks_without_lists = Task.query.filter(~Task.lists.any()).all()
    ungrouped_tasks_count = len(tasks_without_lists)

    # Объединяем данные в один словарь для удобства передачи в шаблон
    to_do_groups = {
        'myday_count': 5,
        'tasks_count': ungrouped_tasks_count,
        'groups': group_data,
        'ungrouped_lists': ungrouped_data
    }

    # print(f'list_groups: {to_do_groups}')
    return to_do_groups


@app.route('/add_list', methods=['POST'])
def add_object():
    object_name = request.form['name']
    object_type = request.form['type']

    if object_type == 'list':
        new_object = List(name=object_name)
    elif object_type == 'group':
        new_object = Group(name=object_name)
    else:
        return jsonify({'success': False, 'message': 'Неизвестный тип объекта'})

    db.session.add(new_object)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Объект добавлен'})


@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    list_id = request.form.get('list_id', 'default')
    task_id = request.form.get('task_id', None)
    print(f'add_task: title: {title}, list_id: {list_id}, task_id: {task_id}')

    new_task = Task(title=title)

    if task_id:
        target_task = db.session.get(Task, task_id)
        if target_task:
            new_task.task_type = 'subtask'
            target_task.subtasks.append(new_task)
            db.session.add(target_task)
            db.session.commit()
            task_data = build_task_structure(target_task)
            task_data['expanded'] = True
            new_task_div = render_template('to_do/tasks.html', tasks=[task_data])
            return jsonify({'success': True, 'div': new_task_div, 'div_id': task_data['id']})

    if list_id in ['default', 'myday', 'tasks']:
        new_task = Task(title=title)
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Задача успешно добавлена в общий список'})

    target_list = List.query.get(list_id)
    if target_list and not task_id:
        # Добавляем задачу в список
        target_list.tasks.append(new_task)
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Задача успешно добавлена'})

    return jsonify({'success': False, 'message': 'Недостаточно данных для добавления задачи'})


@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    list_id = request.args.get('list_id')
    tasks_data = []

    if list_id in ['default', 'myday', 'tasks']:
        # Задачи без списка и не имеющие тип
        tasks_query = Task.query.filter(
            ~Task.lists.any(),
            or_(Task.task_type != 'subtask', Task.task_type == None)
        ).all()
    else:
        tasks_query = Task.query.filter(Task.lists.any(List.id == list_id)).all()  # Задачи определенного списка

    for task in tasks_query:
        tasks_data.append(build_task_structure(task))

    # print(f'get_tasks: tasks_data: {tasks_data}')
    # Генерация HTML для списка задач, предполагаем наличие подходящего шаблона
    tasks_html = render_template('to_do/tasks.html', tasks=tasks_data)
    return jsonify({'html': tasks_html})


@app.route('/get_groups')
def get_groups():
    # Вернуть HTML для обновления списка групп
    groups_data = list_groups()  # Предполагаем, что list_groups возвращает словарь с данными
    rendered_html = render_template('to_do/groups.html', to_do_groups=groups_data)
    return jsonify({'html': rendered_html})


def build_task_structure(task):
    div_time = datetime.now().strftime("%Y%m%d%H%M%S")
    random_id = random.randint(1000, 9999)
    task_data = {
        'id': f'{task.id}_{div_time}{random_id}',
        'task_id':  task.id,
        'title': task.title,
        'type': 'accordion' if task.subtasks else 'regular',
        'children': []
    }
    # print(task_data)
    for subtask in task.subtasks:
        task_data['children'].append(build_task_structure(subtask))
    task_data['subtasks_count'] = len(task.subtasks)
    return task_data


@app.route('/get_tasks_edit', methods=['GET'])
def get_tasks_edit():
    task_id = request.args.get('task_id')
    task = Task.query.get(task_id)
    task_data = {}
    if task:
        task_data['id'] = task_id
        task_data['title'] = task.title
        task_data['note'] = task.description
        if task.status:
            task_data['status'] = task.status.name
        if task.priority:
            task_data['priority'] = task.priority.name
        if task.interval:
            task_data['interval'] = task.interval.name
        if task.due_date:
            task_data['due_date'] = task.due_date.strftime('%Y-%m-%d')
        if task.subtasks:
            task_data['subtasks'] = task.subtasks
    task_edit_html = render_template('to_do/task_edit.html', task=task_data)
    return jsonify({'html': task_edit_html})


@app.route('/test')
def test():
    data = list_groups()
    # Рендеринг HTML шаблона с данными
    return render_template('ToDoList.html', to_do_groups=data)


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
    delimiter = data.get('delimiter', '')

    cleaned_original_text = original_text.lower()
    cleaned_user_text = user_text.lower()

    # Разделение строк на слова по пробелам
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
        # print(f'new_message: target_module: {target_module}')
        match module_type:
            case 'component':
                div_time = datetime.now().strftime("%Y%m%d%H%M%S")
                random_id = random.randint(1000, 9999)
                component_info = find_info(target_module, text)
                component_info['id'] = f'{div_time}{random_id}'
                # print(f'new_message: component_info: {component_info}')
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
    # print(f'action_module_processing: module_path: {module_path}')
    try:
        with open(module_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        print(f'action_module_processing: {e}')
        return None

    # print(f'action_module_processing: data: {data}')

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
