import requests
import json
import time
import google.generativeai as genai


def load_settings():
    # Настройка прокси-сервера
    # proxy_type = 'https'
    proxy_host = "165.22.36.164"
    proxy_port = 10006
    proxy_type = 'https'
    # proxy_host = "69.75.143.13"
    # proxy_port = 80
    # proxy_type = 'socks5'
    # proxy_host = "162.241.45.22"
    # proxy_port = 36213
    proxies = {proxy_type: f"{proxy_type}://{proxy_host}:{proxy_port}"}

    # получение ключа
    try:
        with open('config.txt', 'r') as file:
            for line in file:
                if 'API_KEY_GEMINI' in line:
                    api_key = line.split('=')[1].strip()
                    genai.configure(api_key=api_key)
                    break  # Выходим из цикла после нахождения ключа
    except FileNotFoundError:
        print("Файл 'config.txt' не найден.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    if not api_key:
        print('Нет API ключа: API_KEY_GEMINI')

    return api_key, proxies

'''# Тестовый запрос для проверки прокси
try:
    print("Проверяем подключение через прокси...")
    start_time = time.time()
    test_response = requests.get("https://httpbin.org/ip", proxies=proxies)
    elapsed_time = time.time() - start_time
    print(f"Тестовый ответ: {test_response.status_code}, время: {elapsed_time:.2f} секунд")
    print(test_response.text)
except Exception as e:
    print(f"Ошибка при тестировании прокси: {e}")
    exit()'''


def gemini_proxy_response(text):
    print(f'gemini_proxy_response: {text}')
    # Подготовка данных для запроса
    GOOGLE_API_KEY, proxies = load_settings()
    url = 'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=' + GOOGLE_API_KEY
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {"parts": [{"text": text}]}
        ]
    }

    print("Отправка запроса...")
    # print("URL:", url)

    # Отправка запроса
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, data=json.dumps(data), proxies=proxies)
        elapsed_time = time.time() - start_time
        print(f"Статус ответа API: {response.status_code}, время: {elapsed_time:.2f} секунд")
       # print(response.text)

        # Обработка и вывод ответа
        response_data = json.loads(response.text)
        if response_data.get("candidates"):
            content = response_data["candidates"][0]["content"]["parts"][0]["text"]
            result = content
            # print("Текст ответа:", content)
        else:
            error_message = response_data["error"]["message"]
            result = error_message
    except Exception as e:
        result = f"Произошла ошибка при отправке запроса: {e}"
        # print(result)

    return result.replace(GOOGLE_API_KEY, '')


def gemini_no_proxy_response(text):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(text)
        for chunk in response:
            print(chunk.text)
    except Exception as e:
        print(f'ai_response: {e}')