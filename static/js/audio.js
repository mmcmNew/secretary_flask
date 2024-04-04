// Функция для начала воспроизведения
function startAudio(audioId) {
    let audioContainer = document.getElementById(audioId + "_audioContainer");
    let audio = new Audio(audioContainer.getAttribute('data-audio-src'));

    // Установка громкости и позиции
    audio.volume = parseFloat(document.getElementById(audioId + "_audio_volume").value);

    audio.addEventListener('loadedmetadata', function() {
        // Теперь можно безопасно устанавливать currentTime
        audio.currentTime = parseFloat(document.getElementById(audioId + "_audio_progress").value) * audio.duration / 100;
    });

    // Начало воспроизведения
    audio.play();

    // Обработчик события завершения воспроизведения
    audio.onended = function() {
        // console.log("Аудио " + audioId + " завершено");
        audioContainer.dispatchEvent(new CustomEvent('audioEnded', { detail: audioId }));
        // Другие действия после завершения воспроизведения
    };

    // Сохраняем объект Audio
    audioContainer.audio = audio;
}

// Функция для остановки аудио
function stopAudio(audioId) {
    let audioContainer = document.getElementById(audioId + "_audioContainer");
    let audio = audioContainer.audio;
    if (audio) {
        audio.pause();
        audio.currentTime = 0;
        delete audioContainer.audio;
    }
}

// Функция для закрытия аудиоплеера
function closeAudioPlayer(audioId) {
    let audioContainer = document.getElementById(audioId + "_audioContainer");
    stopAudio(audioId);  // Остановка воспроизведения перед закрытием
    audioContainer.parentNode.removeChild(audioContainer);  // Удаление контейнера
}

// Слушатели событий для кнопок
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('toolsPanel').addEventListener('click', function(event) {
        let target = event.target;
        let audioId = target.id.split('_')[0];
        if (target.classList.contains('startAudio')) {
            startAudio(audioId);
        } else if (target.classList.contains('stopAudio')) {
            stopAudio(audioId);
        } else if (target.classList.contains('closeAudio')) {
            closeAudioPlayer(audioId);
        }
    });

    // Слушатель событий для изменения громкости
    document.getElementById('toolsPanel').addEventListener('input', function(event) {
        if (event.target.classList.contains('audio-volume')) {
            let audioId = event.target.id.split('_')[0];
            let audioContainer = document.getElementById(audioId + "_audioContainer");
            let audio = audioContainer.audio;
            if (audio) {
                audio.volume = parseFloat(event.target.value);
            }
        }
    });

    // Слушатель событий для перемотки
    document.getElementById('toolsPanel').addEventListener('input', function(event) {
        if (event.target.classList.contains('audio-progress')) {
            let audioId = event.target.id.split('_')[0];
            let audioContainer = document.getElementById(audioId + "_audioContainer");
            let audio = audioContainer.audio;
            if (audio) {
                audio.currentTime = parseFloat(event.target.value) * audio.duration / 100;
            }
        }
    });
});
