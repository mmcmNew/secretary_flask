function playTextUsingServerTTS(text, buttonElement, progressElement) {
     return new Promise((resolve, reject) => {
        buttonElement.html('<span class="spinner-border spinner-border-sm"></span>'); // Замена кнопки на спиннер
        var pauseSVG = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16"><path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5m5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5"/></svg>';
        var playSVG = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16"><path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393"/></svg>'
        // Если аудио уже воспроизводится, останавливаем его
        if (buttonElement.data('audio')) {
            buttonElement.data('audio').pause();
        }

        // Настройка AJAX запроса
        $.ajax({
            type: 'POST',
            url: '/generate-tts',
            data: { text: text },
            success: function(response) {
                var audioUrl = response.audioUrl;
                var audio = new Audio(audioUrl);

                // Сохраняем аудио в элемент кнопки для последующего доступа
                buttonElement.data('audio', audio);

                // Слушатель для события 'canplaythrough'
                audio.addEventListener('canplaythrough', () => {
                    buttonElement.html(pauseSVG); // Замена спиннера на кнопку паузы
                });

                // Слушатель для события 'timeupdate'
                audio.addEventListener('timeupdate', () => {
                    var percentage = (audio.currentTime / audio.duration) * 100;
                    progressElement.style.width = percentage + '%';
                });

                // Слушатель для события 'ended'
                audio.addEventListener('ended', () => {
                    progressElement.style.width = '0%';
                    buttonElement.html(playSVG); // Возврат к кнопке воспроизведения
                    resolve(); // Разрешаем Promise по завершении воспроизведения
                });

                // Обработка нажатия на кнопку
                buttonElement.off('click').click(() => {
                    if (audio.paused) {
                        audio.play();
                        buttonElement.html(pauseSVG);
                    } else {
                        audio.pause();
                        buttonElement.html(playSVG);
                    }
                });

                audio.play();
            },
            error: function(error) {
                reject(error); // Отклоняем Promise в случае ошибки
            }
        });
    });
}

$(document).on('click', '.play-audio-button', function() {
    var messageText = $(this).closest('.chat-message-content').find('.chat-message-text').text();
    var progressBar = $(this).next('.audio-progress')[0];
    playTextUsingServerTTS(messageText, $(this), progressBar);
});

function generateAudioURLFromText(text) {
    return new Promise((resolve, reject) => {
        $.ajax({
            type: 'POST',
            url: '/generate-tts',
            data: { text: text },
            success: function(response) {
                resolve(response.audioUrl);
            },
            error: function(error) {
                reject(error);
            }
        });
    });
}