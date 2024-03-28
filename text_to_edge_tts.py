from datetime import datetime
import os
import asyncio
import random
import time

import edge_tts


def tts(text):
    save_path = os.path.join(os.path.dirname(__file__))
    os.makedirs(save_path, exist_ok=True)
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    random_id = random.randint(1000, 9999)
    edge_filename = os.path.join('static', 'temp', f'edge_audio_{current_time}_{random_id}.mp3')
    edge_output_filename = os.path.join(save_path, edge_filename)
    speed = 40
    tts_voice = 'ru-RU-SvetlanaNeural-Female'

    tts_text = text.replace('*', '')
    try:
        if os.path.exists(edge_output_filename):
            os.remove(edge_output_filename)
        if speed >= 0:
            speed_str = f"+{speed}%"
        else:
            speed_str = f"{speed}%"
        t0 = time.time()
        asyncio.run(
            edge_tts.Communicate(
                tts_text, "-".join(tts_voice.split("-")[:-1]), rate=speed_str
            ).save(edge_output_filename)
        )
        t1 = time.time()
        edge_time = t1 - t0
        print(f'edge_tts: Time: {edge_time}')
        # info = f"Успешно edge-tts"
        # print(info)
        return edge_filename
    except EOFError:
        info = (
            "Похоже, что вывод edge-tts не соответствует действительности. "
            "Это может произойти при несовпадении входного текста и спикера. "
            "Например, вы ввели русский текст, но выбрали не русский?"
        )
        print(info)
        return None
    except Exception as e:
        info = f'edge_tts: {e}'
        print(info)
        return None


if __name__ != '__main__':
    print("start_main")
