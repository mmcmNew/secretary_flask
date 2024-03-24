from datetime import datetime

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

messages = [{'name': 'Me', 'avatar': 'me.png', 'time': '12:10',
             'text': 'Значимость этих проблем настолько очевидна, что новая модель организационной деятельности обеспечивает актуальность ключевых компонентов планируемого обновления. Соображения высшего порядка, а также рамки и место обучения кадров в значительной степени обуславливает создание существующих финансовых и административных условий. Соображения высшего порядка, а также консультация с профессионалами из IT способствует подготовке и реализации ключевых компонентов планируемого обновления.',
             'position': 'r'},
            {'name': 'Gemini', 'avatar': 'ai2.png', 'time': '12:10', 'text': 'Случайное сообщение 2', 'position': 'l'},
            {'name': 'Secretary', 'avatar': 'ai.png', 'time': '12:10', 'text': 'Случайное сообщение 3', 'position': 'l',
             'image': 'Designer.jpeg'},
            {'name': 'Me', 'avatar': 'me.png', 'time': '12:10', 'text': 'Случайное сообщение 4', 'position': 'r'},
            {'name': 'Secretary', 'avatar': 'ai.png', 'time': '12:10', 'text': 'Случайное сообщение 5',
             'position': 'l'},
            {'name': 'Gemini', 'avatar': 'ai2.png', 'time': '12:10', 'text': 'Случайное сообщение 6', 'position': 'l'},
            {'name': 'Me', 'avatar': 'me.png', 'time': '12:10', 'text': 'Случайное сообщение 7', 'position': 'r'},
            {'name': 'Secretary', 'avatar': 'ai.png', 'time': '12:10', 'text': 'Случайное сообщение 8',
             'position': 'l'},
            {'name': 'Me', 'avatar': 'me.png', 'time': '12:10', 'text': 'Случайное сообщение 9', 'position': 'r'},
            {'name': 'Gemini', 'avatar': 'ai2.png', 'time': '12:10', 'text': 'Случайное сообщение 10', 'position': 'l'},
            {'name': 'Me', 'avatar': 'me.png', 'time': '12:10', 'text': 'Случайное сообщение 11', 'position': 'r'},
            ]


@app.route('/')
def home():
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

    html_content = render_template('index.html', tabs=tabs, messages=messages, commands=commands)
    return html_content


@app.route('/test')
def test():
    return render_template('test.html', messages=messages)


@app.route('/new-message', methods=['POST'])
def new_message():
    time_now = datetime.now()
    current_time = time_now.strftime("%H:%M")
    if request.method == 'POST':
        # Если функция вызвана как обработчик маршрута, получаем сообщение из запроса
        text = request.form['message']
        print(text)
        message = {'name': 'Me',
                   'avatar': 'me.png',
                   'time': current_time,
                   'text': text,
                   'position': 'r'}
        chat_message = render_template('message_template.html', message=message)
    else:
        # Если функция вызвана вручную из другого места кода, используем переданный параметр
        data = request.args.get('message')
        message = {'name': data['name'],
                   'avatar': data['avatar'],
                   'time': current_time,
                   'text': data['message'],
                   'position': 'l'}
        chat_message = render_template('chat-message.html', message)

    return jsonify({'div': chat_message})


if __name__ == '__main__':
    app.run(debug=True)
