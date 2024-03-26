import re
import sqlite3
from datetime import datetime

from modules.geminiVPN import gemini_proxy_response

modules = {'timers': ['таймеры'],
           'timer': ['таймер', 'напомни'],
           'metronome': ['метроном'],
           'memory': ['память'],
           'ai_chat': ['расскажи'],
           'trading_journal': ['торгов', 'журнал']}

commands_list = {'start': ['запусти', 'поставь', 'установи'],
                 'stop': ['остановить', 'заверши', 'останови'],
                 'reload': ['измени'],
                 'create': ['запиши', 'добавь запись'],
                 'append': ['допиши', ],
                 'edit': ['перезапиши']}

command_information = {'name': ['назван'],
                       'trading_day': ['сегодня'],
                       'bias': ['настро'],
                       'news': ['новос'],
                       'session': ['сесси'],
                       'model': ['модел'],
                       'reason': ['причин'],
                       'result': ['резул'],
                       'comment': ['коммент']}

buttons = ['timer start',
           'timers stop',
           'metronome start',
           'metronome stop',
           'memory start']


def parse_time(text):
    print(text)
    if 'полчаса' in text:
        result = '00:30:00'
        return result

    time_units = {"час": 0, "минут": 0, "секунд": 0}
    numbers_in_text = [int(num) for num in re.findall(r'\d+', text)]

    for unit in time_units.keys():
        if unit in text:
            try:
                time_units[unit] = numbers_in_text.pop(0)
            except (ValueError, IndexError):
                continue
    result = f'{time_units["час"]:02}:{time_units["минут"]:02}:{time_units["секунд"]:02}'
    return result


def find_command_type(command):
    global commands_list
    command_type = None
    for key, values in commands_list.items():
        if command_type:
            break
        for value in values:
            if value in command:
                command_type = key
                break
    return command_type


def find_info(text):
    # Уникальный разделитель, который маловероятно встретить в тексте
    delimiter = "||"
    replacements_made = None
    # Заменяем слова на ключевые слова с разделителем
    for key, values in command_information.items():
        for value in values:
            # Находим позицию первого вхождения ключевого слова
            start = text.find(value)
            if start != -1:
                # Находим позицию следующего пробела после ключевого слова
                end = text.find(' ', start)
                if end == -1:
                    end = len(text)  # Если пробел не найден, заменяем до конца текста
                # Заменяем весь фрагмент ключевым словом и разделителем
                text = text[:start] + delimiter + key + text[end:]
                replacements_made = True
                break  # Прекращаем поиск после первой замены для данного ключа

    if not replacements_made:
        return {}
    # Разделяем текст по разделителю
    split_text = text.split(delimiter)

    # Собираем словарь, где ключ - это ключевое слово, а значение - текст до следующего ключа
    result = {}
    for i, segment in enumerate(split_text[1:], start=1):  # Пропускаем первый элемент, так как он перед первым ключевым словом
        key = segment.split()[0]  # Первое слово - ключ
        value = ' '.join(segment.split()[1:])  # Остальная часть - значение
        result[key] = value

    return result


def process_command(command):
    global modules, commands_list
    if command is None or modules is None or commands_list is None:
        return None

    target_module = None
    # Определяем модуль по словарю. Словарь Модуль:[Список слов активации]
    for key, values in modules.items():
        if target_module:
            break
        for module_command in values:
            if module_command in command:
                target_module = key
                break

    if target_module is None:
        return None

    # Если целевой модуль ai передаем всю команду
    if target_module == 'ai_chat':
        text = gemini_proxy_response(command)
        ai_message = {'user_id': 3, 'text': text}
        return ai_message

    # Получаем результат от модулей
    result = load_modules({'target_module': target_module, 'text': command})
    if result is None:
        return None

    ai_message = {'user_id': 2, 'text': result['text']}

    return ai_message


def save_to_base(message):
    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")
        table_name = message.get('table_name', '')
        columns = []
        values = []
        del message['table_name']
        if table_name == 'TradingJournal':
            message['date'] = current_date
            trading_day = message.get('trading_day', current_date)
            columns = ['trading_day', 'time']
            values = [trading_day, current_time]
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
        return 1, ''
    except Exception as e:
        return None, f'{e}'


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
        return 1, ''
    except Exception as e:
        return None, f'Append to base: {e}'


def load_modules(command):
    global commands_list
    module_name = command.get('target_module', None)
    command_text = command.get('text', None)
    if module_name is None:
        return None
    # Определяем команду по словарю. Словарь Действие:[Список слов активации]
    match module_name:
        case 'trading_journal':
            print(f'command_text: {command_text}')
            print(f'module_name: {module_name}')
            command_type = find_command_type(command_text)
            command_info = find_info(command_text)
            command_info['table_name'] = 'TradingJournal'
            if command_type == 'create':
                result, error = save_to_base(command_info)
                if not result:
                    print(error)
                    return {'text': error}
                return {'text': 'Запись добавлена в журнал'}
            if command_type == 'append':
                result, error = append_to_base(command_info)
                if not result:
                    print(error)
                    return {'text': 'Ошибка записи в журнал'}
                return {'text': 'Запись добавлена в журнал'}
    return {'text': f'Команда {command_text} не обработана'}
    timer_time = parse_time(command)  # парсим время во фразе
    found_numbers = re.findall(r'\d+', command)
