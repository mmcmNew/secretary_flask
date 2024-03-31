import os
import re
import sqlite3
from datetime import datetime

modules = {
    'timer': {'words': ['таймер', 'напомни'], 'commands_list': ['start', 'stop', 'edit', 'del'], 'info': ['name']},
    'metronome': {'words': ['метроном'], 'commands_list': ['start', 'stop', 'edit', 'del'], 'info': ['name']},
    'memory': {'words': ['память']},
    'ai_chat': {'words': ['расскажи']},
    'trading_journal': {'words': ['трейд', 'торгов'], 'commands_list': ['create', 'append', 'edit', 'del'],
                        'info': ['trading_day', 'bias', 'news', 'session', 'model', 'reason', 'result', 'comment']},
    'diary': {'words': ['дневник'], 'commands_list': ['create', 'append', 'edit', 'del'],
              'info': ['reason', 'result', 'lessons', 'comment']},
    'project_journal': {'words': ['разработ'], 'commands_list': ['create', 'append', 'edit', 'del'],
                        'info': ['project_name', 'step', 'comment']},
    'productivity': {'words': ['фокусир'], 'commands_list': ['start', 'stop'],
                     'actions': []}}

commands_list = {'start': ['запусти', 'поставь', 'установи'],
                 'stop': ['остановить', 'заверши', 'останови'],
                 'create': ['запиши', 'добавь запись'],
                 'append': ['допиши', 'до пиши', 'да пиши'],
                 'edit': ['перезапиши'],
                 'del': ['удали']}

command_information = {'name': ['назван', 'назови', 'напомни'],
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
                       'step': ['этап']}

buttons = ['timer start',
           'timers stop',
           'metronome start',
           'metronome stop',
           'memory start']


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
    replacements_made = None
    print(f'find_info: text: {text}')
    # Заменяем слова на ключевые слова с разделителем
    for info_type in modules[module_name]['info']:
        for value in command_information[info_type]:
            # Находим позицию первого вхождения ключевого слова
            start = text.lower().find(value)
            if start != -1:
                # Находим позицию следующего пробела после ключевого слова
                end = text.find(' ', start)
                if end == -1:
                    end = len(text)  # Если пробел не найден, заменяем до конца текста
                # Заменяем весь фрагмент ключевым словом и разделителем
                text = text[:start] + delimiter + info_type + text[end:]
                replacements_made = True
                break  # Прекращаем поиск после первой замены для данного ключа

    result = {}
    if module_name == 'metronome':
        matches = re.findall(r'\d+', text)
        bpm = int(matches[0]) if matches else 120
        result = {'bpm': f'{bpm}'}
        print(result)
    if not replacements_made:
        return result
    # Разделяем текст по разделителю
    split_text = text.split(delimiter)

    # Собираем словарь, где ключ - это ключевое слово, а значение - текст до следующего ключа
    for i, segment in enumerate(split_text[1:],
                                start=1):  # Пропускаем первый элемент, так как он перед первым ключевым словом
        key = segment.split()[0]  # Первое слово - ключ
        value = ' '.join(segment.split()[1:])  # Остальная часть - значение
        result[key] = value
    print(f'find_info: {result}')
    return result


def find_target_module(command):
    global modules
    if command is None or modules is None:
        return None

    target_module = None
    # Определяем модуль по словарю. Словарь Модуль:{[Список слов активации], [Список команд модуля], [Список информации]}
    earliest_occurrence = len(command) + 1
    for key, values in modules.items():
        for module_command in values['words']:
            position = command.lower().find(module_command)
            if position != -1 and position < earliest_occurrence:
                earliest_occurrence = position
                target_module = key
    # target_module установлен в первый модуль, найденный в command_text

    if target_module is None:
        return None

    return target_module


def save_to_base_modules(command):
    global commands_list
    module_name = command.get('target_module', None)
    command_text = command.get('text', None)
    files_list = command.get('files', None)
    if module_name is None:
        return None
    # Получаем тип команды
    result = ''
    command_type = find_command_type(module_name, command_text)
    print(f'save_to_base: command_type: {command_type}')
    match command_type:
        case 'create':
            command_info = find_info(module_name, command_text)
            command_info['table_name'] = module_name
            save_result = save_to_base(command_info)
            result = save_result
            if files_list:
                save_result = save_files({'files_list': files_list, 'dir_name': module_name})
                result += f'{save_result}'

        case 'append':
            command_info = find_info(module_name, command_text)
            command_info['table_name'] = module_name
            save_result = append_to_base(command_info)
            result = save_result
            if files_list:
                save_result = save_files({'files_list': files_list, 'dir_name': module_name})
                result += f'{save_result}'
        case _:
            return {'text': f'Команда {command_text} не обработана'}

    return {'text': result}


def save_to_base(message):
    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        table_name = message.get('table_name', '')
        columns = []
        values = []
        print(f'save_to_base: message: {message}')
        del message['table_name']
        if table_name == 'trading_journal':
            message['date'] = current_date
            trading_day = message.get('trading_day', current_date)
            message['trading_day'] = trading_day
            message['time'] = current_time
        if table_name == 'diary' or table_name == 'project_journal':
            message['date'] = current_date
            message['time'] = current_time
            # Собираем названия столбцов и их значения из словаря message
        print(message)
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
    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        current_time = datetime.now().strftime("%H:%M")
        table_name = message.get('table_name', None)
        del message['table_name']
        if table_name is None or message == {}:
            return None, f'Уточните что нужно добавить в журнал'
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


def save_files(files):
    try:
        files_list = files.get('files_list', None)
        dir_name = files.get('dir_name', None)
        print(f'save_files: files_list: {files_list}, dir_name: {dir_name}')
        if files_list is None or dir_name is None:
            return 'Не получены файлы для загрузки'
        print(f'save_files: files_list: {files_list}, dir_name: {dir_name}')
        if files_list:
            current_month = datetime.now().strftime('%m')
            save_path = os.path.join(os.path.dirname(__file__), 'static', 'images', dir_name, current_month)
            os.makedirs(save_path, exist_ok=True)
            current_date = datetime.now().strftime("%Y-%m-%d")
            i = 0
            print(f'load_modules: files_list: {files_list}')
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
                i += 1
        result = 'Файлы загружены. '
        return result
    except Exception as e:
        result = f'Файлы не загружены: {e}. '
        return result


if __name__ != '__main__':
    print("start_main")
