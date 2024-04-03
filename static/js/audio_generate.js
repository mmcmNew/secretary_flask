function bindAudioListeners(audio, buttonElement, progressElement) {
    audio.addEventListener('canplaythrough', () => {
        buttonElement.html('<i class="bi bi-pause-fill"></i>'); // Замена спиннера на кнопку паузы
        buttonElement.prop('disabled', false);
    });

    audio.addEventListener('timeupdate', () => {
        var percentage = (audio.currentTime / audio.duration) * 100;
        progressElement.style.width = percentage + '%';
    });

    audio.addEventListener('ended', () => {
        progressElement.style.width = '0%';
        buttonElement.html('<i class="bi bi-play-fill"></i>'); // Возврат к кнопке воспроизведения

        buttonElement.trigger('audioTextEnded', [buttonElement.attr('id')]); // триггерим событие 'audioEnded' с ID кнопки
    });
}

function playTextUsingServerTTS(audio, buttonElement, progressElement) {
    bindAudioListeners(audio, buttonElement, progressElement);

    if (audio.paused) {
        audio.play();
        buttonElement.html('<i class="bi bi-pause-fill"></i>');
    } else {
        audio.pause();
        buttonElement.html('<i class="bi bi-play-fill"></i>');
    }
}

function generateAudioForButton(buttonElement) {
    var messageId = buttonElement.attr('id').split('_')[0];

    var messageTextElement = $('#' + messageId + '_messageText');
    var messageText = messageTextElement.text();

    // Замена кнопки на спиннер
    buttonElement.html('<span class="spinner-border spinner-border-sm"></span>').prop('disabled', true);

    return new Promise((resolve, reject) => {
        generateAudioURLFromText(messageText).then(audioUrl => {
            var audio = new Audio(audioUrl);
            buttonElement.data('audio', audio);
            buttonElement.html('<i class="bi bi-play-fill"></i>'); // Возврат к иконке воспроизведения
            buttonElement.prop('disabled', false);
            resolve(audio);
        }).catch(error => {
            console.error('Error generating audio:', error);
            reject(error);
        });
    });
}

$(document).on('click', '.play-audio-button', function() {
    var buttonElement = $(this);
    var audio = buttonElement.data('audio');
    var progressBar = $('#' + buttonElement.attr('id').split('_')[0] + '_textProgress')[0];

    if (!audio) {
        generateAudioForButton(buttonElement).then(generatedAudio => {
            playTextUsingServerTTS(generatedAudio, buttonElement, progressBar);
        });
    } else {
        playTextUsingServerTTS(audio, buttonElement, progressBar);
    }
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

