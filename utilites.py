import os
import random
import re
import sqlite3
from datetime import datetime
from config import db_name

modules = {
    'tasks': {'words': ['задач'], 'commands_list': ['create', 'filter', 'edit', 'del'],
              'info': ['subtask', 'task_name', 'status', 'list'], 'type': 'task'},
    'timer': {'words': ['таймер', 'напомни'], 'commands_list': ['start', 'stop', 'edit', 'del'],
              'info': ['name', 'time'], 'type': 'component'},
    'metronome': {'words': ['метроном'], 'commands_list': ['start', 'stop', 'edit', 'del'],
                  'info': ['name', 'bpm', 'count'], 'type': 'component'},
    'memory': {'words': ['памят'], 'info': ['name', 'interval', 'count'], 'type': 'component'},
    'ai_chat': {'words': ['расскажи'], 'type': 'ai_chat'},
    'trading_journal': {'words': ['трейд', 'торгов'], 'commands_list': ['create', 'append', 'edit', 'del'],
                        'info': ['trading_day', 'bias', 'news', 'session', 'model', 'reason', 'result', 'comment'],
                        'type': 'journal'},
    'backtest_journal': {'words': ['тест'], 'commands_list': ['create', 'append', 'edit', 'del'],
                         'info': ['trading_day', 'bias', 'news', 'session', 'model', 'reason', 'result', 'comment'],
                         'type': 'journal'},
    'diary': {'words': ['дневник'], 'commands_list': ['create', 'append', 'edit', 'del'],
              'info': ['reason', 'score', 'lessons', 'comment'], 'type': 'journal'},
    'review_journal': {'name': 'отзывов', 'words': ['отзыво'],
                       'commands_list': ['create', 'append', 'edit', 'del'],
                       'info': ['name', 'score', 'author', 'problems', 'facts', 'features', 'new_info', 'comment'],
                       'type': 'journal'},
    'project_journal': {'words': ['разработ'], 'commands_list': ['create', 'append', 'edit', 'del'],
                        'info': ['project_name', 'step', 'comment'], 'type': 'journal'},
    'productivity': {'words': ['фокусир'], 'commands_list': ['start', 'stop'], 'type': 'action_module'},
    'relax': {'words': ['расслабл'], 'commands_list': ['start', 'stop'], 'type': 'action_module'},
    'demo': {'words': ['демонстрац'], 'commands_list': ['start', 'stop'], 'type': 'action_module'}}

commands_list = {'start': ['запусти', 'поставь', 'установи'],
                 'stop': ['остановить', 'заверши', 'останови'],
                 'create': ['запиши', 'добавь запись', 'создай'],
                 'append': ['допиши', 'до пиши', 'да пиши'],
                 'edit': ['перезапиши', 'отметь', 'добавь'],
                 'del': ['удали'],
                 'filter': ['озвучь', 'перечисли']}

command_information = {'name': ['назван', 'назови', 'напомни'],
                       'author': ['автор'],
                       'problems': ['проблем'],
                       'facts': ['факт'],
                       'features': ['особенност'],
                       'new_info': ['новые знания'],
                       'trading_day': ['сегодня'],
                       'bias': ['настро'],
                       'news': ['новос'],
                       'session': ['сесси'],
                       'model': ['модел'],
                       'reason': ['причин'],
                       'result': ['резул'],
                       'comment': ['коммент'],
                       'lessons': ['урок'],
                       'project_name': ['проект'],
                       'step': ['этап'],
                       'score': ['оценк'],
                       'status': ['отметь', 'статус'],
                       'task_name': ['задач'],
                       'subtask': ['подзадач', 'под задач'],
                       'list': ['список'], }

command_num_information = {'bpm': ['частота', 'чистота'],
                           'interval': ['интервал'],
                           'count': ['количество']}


def parse_time(text):
    print(text)
    if 'полчаса' in text:
        return ['00', '30', '00']

    time_units = {"час": 0, "минут": 0, "секунд": 0}
    numbers_in_text = [int(num) for num in re.findall(r'\d+', text)]

    for unit in time_units.keys():
        if unit in text:
            try:
                time_units[unit] = numbers_in_text.pop(0)
            except (ValueError, IndexError):
                continue
    result = [time_units["час"], time_units["минут"], time_units["секунд"]]
    return result


def find_command_type(module_name, command):
    global commands_list, modules
    command_type = None
    print(f'find_command_type: command: {command}')
    for commands_types in modules[module_name]['commands_list']:
        if command_type:
            break
        for value in commands_list[commands_types]:
            if value in command.lower():
                command_type = commands_types
                break
    return command_type


def find_info(module_name, text):
    # Уникальный разделитель, который маловероятно встретить в тексте
    delimiter = "||"
    replacements_made = False
    print(f'find_info: text: {text}')
    result = {}
    # Заменяем слова на ключевые слова с разделителем
    command_info_dict = command_information | command_num_information  # складываем 2 словаря для нахождения ключей
    # проверка условия если в modules[module_name]['info'] есть ключевое слово comment то проверяются
    # значения из словаря command_info_dict['comment'] и заменяется его значение значением ключа comment и
    # запоминается позиция вхождения ключевого слова в тексте
    comment_start = len(text)
    if 'comment' in modules[module_name]['info']:
        for value in command_info_dict['comment']:
            # Находим позицию первого вхождения ключевого слова
            comment_start = text.lower().find(value)
            if comment_start != -1:
                # Находим позицию следующего пробела после ключевого слова
                end = text.find(' ', comment_start)
                if end == -1:
                    end = len(text)  # Если пробел не найден, заменяем до конца текста
                # Заменяем весь фрагмент ключевым словом и разделителем
                text = text[:comment_start] + delimiter + 'comment' + text[end:]
                replacements_made = True
                break  # Прекращаем поиск после первой замены для данного ключа

    for info_type in modules[module_name]['info']:
        if info_type == 'time':
            result = {'time': parse_time(text)}
            continue
        if info_type == 'comment':
            continue
        for value in command_info_dict[info_type]:
            # Находим позицию первого вхождения ключевого слова до вхождения ключа comment
            start = text.lower().find(value, 0, comment_start)
            if start != -1:
                # Находим позицию следующего пробела после ключевого слова
                end = text.find(' ', start)
                if end == -1:
                    end = comment_start  # Если пробел не найден, заменяем до конца текста
                # Заменяем весь фрагмент ключевым словом и разделителем
                text = text[:start] + delimiter + info_type + text[end:]
                replacements_made = True
                break  # Прекращаем поиск после первой замены для данного ключа

    if module_name == 'memory':
        cards_count = int(result.get('count', 50))
        result['count'] = cards_count
        result['items'] = generate_cards(cards_count)

    if not replacements_made:
        return result

    # Разделяем текст по разделителю
    split_text = text.split(delimiter)

    # Собираем словарь, где ключ - это ключевое слово, а значение - текст до следующего ключа
    for i, segment in enumerate(split_text[1:],
                                start=1):  # Пропускаем первый элемент, так как он перед первым ключевым словом
        key = segment.split()[0]  # Первое слово - ключ
        if key in command_num_information:  # для числовых ключей берем первое число после ключа
            found_numbers = re.findall(r'\d+', segment)
            if found_numbers:
                value = found_numbers[0]
                result[key] = value
                continue
        value = ' '.join(segment.split()[1:])  # Остальная часть - значение
        result[key] = value

    return result


def generate_cards(cards_count=50, cards_type='references', string_words=None):
    items = []
    folder_path = os.path.join('static', 'images', 'memory')
    if cards_type == 'references':
        files = os.listdir(folder_path)
        if not files:
            raise ValueError("В папке нет файлов")
        selected_files = random.choices(files, k=cards_count)
        for file in selected_files:
            name = os.path.splitext(file)[0]
            url = f"memory/{file}"
            items.append({'text': name, 'url': url})
    elif cards_type == 'words':
        delimiter = string_words.get('delimiter', ' ')
        words = string_words['words'].split(delimiter)
        for word in words:
            name = word
            url = f"memory/placeholder.jpg"
            items.append({'text': name, 'url': url})

    return items


def find_target_module(command):
    global modules
    if command is None or modules is None:
        return None

    target_module = None
    # Определяем модуль по словарю.
    # Словарь Модуль:{[Список слов активации], [Список команд модуля], [Список информации]}
    earliest_occurrence = len(command) + 1
    for key, values in modules.items():
        for module_command in values['words']:
            position = command.lower().find(module_command)
            if position != -1 and position < earliest_occurrence:
                earliest_occurrence = position
                target_module = key
    # target_module установлен в первый модуль, найденный в command_text

    if target_module is None:
        return None, None

    module_type = modules[target_module]['type']
    return target_module, module_type


def save_to_base_modules(command):
    global commands_list
    module_name = command.get('target_module', None)
    command_text = command.get('text', None)
    files_list = command.get('files', None)
    save_files_result = None
    command_info = {}
    if module_name is None:
        return None
    # Получаем тип команды
    command_type = find_command_type(module_name, command_text)
    print(f'save_to_base_modules: command_type: {command_type}')
    if files_list:
        save_files_result, files_names = save_files({'files_list': files_list, 'dir_name': module_name})
        if files_names:
            command_info['files'] = ''
            for file_name in files_names:
                command_info['files'] += file_name + ';'
    # print(f'save_to_base_modules: command_info: {command_info}')

    match command_type:
        case 'create':
            command_info.update(find_info(module_name, command_text))
            # command_info = check_keys_in_message(command_info)
            command_info['table_name'] = module_name
            save_result = save_to_base(command_info)
            result = save_result

        case 'append':
            command_info.update(find_info(module_name, command_text))
            # command_info = check_keys_in_message(command_info)
            command_info['table_name'] = module_name
            save_result = append_to_base(command_info)
            result = save_result
        case _:
            return {'text': f'save_to_base_modules: Команда не обработана'}

    if save_files_result:
        result += f' {save_files_result}'
    return {'text': result}


def save_to_base(message):
    table_name = message.get('table_name', '')
    # print(f'save_to_base: message: {message}')
    if table_name:
        del message['table_name']
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        columns = []
        values = []
        if table_name == 'trading_journal':
            trading_day = message.get('trading_day', current_date)
            message['trading_day'] = trading_day
        if table_name in ('diary', 'project_journal', 'backtest_journal', 'trading_journal'):
            message['date'] = f'{current_date} {current_time}'
            message['time'] = current_time
            # Собираем названия столбцов и их значения из словаря message

        # print(f'save_to_base: message: {message}')
        for key, value in message.items():
            try:
                columns.append(key)
                if key == 'comment':
                    value = f'{current_time}: {value}\n'
                values.append(value)

            except Exception as e:
                print(e)
        # Формируем строку запроса
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])})"
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        cursor.execute(query, tuple(values))

        # Сохранение изменений
        connection.commit()
        connection.close()
        result = f'Запись добавлена в {table_name}. '
        return result
    except Exception as e:
        result = f'Ошибка добавления записи в {table_name}: {e}. '
        return result


def append_to_base(message):
    table_name = message.get('table_name', None)
    print(f'append_to_base: message: {message}')
    if table_name:
        del message['table_name']
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        if table_name is None or message == {}:
            return f'Уточните что нужно добавить в журнал'

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        print(f'append_to_base: message: {message}')
        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
        last_row_id = cursor.fetchone()[0]
        update_parts = []
        for key, value in message.items():
            if key == 'comment':
                # Добавление текущего времени к комментарию
                value = f"{current_time}: {value}"
            update_parts.append(f"{key} = COALESCE({key}, '') || ? || '\n'")
            message[key] = value

        update_query = ", ".join(update_parts)

        # Формирование и выполнение запроса на обновление
        query = f"UPDATE {table_name} SET {update_query} WHERE id = ?"

        # Сбор значений для запроса
        values = list(message.values())
        values.append(last_row_id)  # Добавляем идентификатор последней строки к значениям
        cursor.execute(query, values)
        print(f'last_row_id: {last_row_id}')
        print(f'query: {query}')
        print(f'values: {values}')
        # Сохранение изменений
        connection.commit()
        connection.close()
        result = f'Запись дополнена в {table_name}. '
        return result
    except Exception as e:
        result = f'Ошибка при редактировании записи в {table_name}: {e}. '
        return result


def check_keys_in_message(message):
    table_name = message.get('table_name', None)
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    connection.close()

    # Определение столбцов, присутствующих в таблице
    columns_names = [column[1] for column in columns_info]
    keys_to_remove = [key for key in message if key not in columns_names]

    # Удаление неподходящих ключей
    for key in keys_to_remove:
        del message[key]
        print(f'Удален ключ {key} из словаря message т.к. его нет в базе')

    return message


def save_files(files):
    files_names = []
    try:
        files_list = files.get('files_list', None)
        dir_name = files.get('dir_name', None)
        print(f'save_files: files_list: {files_list}, dir_name: {dir_name}')
        if files_list is None or dir_name is None:
            return 'Не получены файлы для загрузки'
        if files_list:
            current_month = datetime.now().strftime('%Y-%m')
            save_path = str(os.path.join(os.path.dirname(__file__), 'static', 'images', dir_name, current_month))
            os.makedirs(save_path, exist_ok=True)
            current_date = datetime.now().strftime("%Y-%m-%d")
            i = 0
            for file_key in files_list:
                file = files_list[file_key]
                if file.filename == '':
                    continue
                file_extension = os.path.splitext(file.filename)[1]
                save_file_name = f'{current_date}[{i}]{file_extension}'
                while os.path.exists(os.path.join(save_path, save_file_name)):
                    i += 1
                    save_file_name = f'{current_date}[{i}]{file_extension}'

                file.save(os.path.join(save_path, save_file_name))
                files_names.append(os.path.join(dir_name, current_month, save_file_name))
                i += 1
        print(f'save_files: files_names: {files_names}')
        result = 'Файлы загружены. '
        return result,  files_names
    except Exception as e:
        result = f'Файлы не загружены: {e}. '
        return result, files_names


if __name__ != '__main__':
    print("start_main")
