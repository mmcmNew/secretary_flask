function togglePlayPause(audioId) {
    let audioContainer = document.getElementById(audioId + "_audioContainer");
    let audio = audioContainer.audio || new Audio(audioContainer.getAttribute('data-audio-src'));
    let playPauseButton = document.getElementById(audioId + "_audio_start"); // Кнопка воспроизведения/паузы
    let progressBar = document.getElementById(audioId + "_audio_progress"); // Получаем ползунок прогресса
    // Обновление или установка аудио

    if (!audioContainer.audio) {
        // Установка слушателей событий только один раз
        audio.addEventListener('loadedmetadata', () => {
            audioContainer.audio = audio;
            // Первоначальная установка currentTime, если ползунок был перемещен до воспроизведения
            audio.currentTime = parseFloat(progressBar.value) * audio.duration / 100;
        });
        audio.addEventListener('timeupdate', () => {
            let progress = (audio.currentTime / audio.duration) * 100;
            progressBar.value = progress;
        });
        audio.onended = () => {
            audioContainer.dispatchEvent(new CustomEvent('audioEnded', { detail: audioId }));
            playPauseButton.innerHTML = '<i class="bi bi-play-fill"></i>';
            progressBar.disabled = false;
        };
    }

    // Проверка и управление воспроизведением/паузой
    if (audio.paused || audio.ended) {
        playPauseButton.innerHTML = '<i class="bi bi-pause-fill"></i>';
        progressBar.disabled = true; // Опционально, если вы хотите сделать ползунок неактивным во время воспроизведения
        // Установка currentTime при каждом снятии с паузы в соответствии с положением ползунка
        if (audio.readyState >= 2) { // Убедимся, что метаданные достаточно загружены для установки currentTime
            audio.currentTime = parseFloat(progressBar.value) * audio.duration / 100;
        }
        audio.play();
    } else {
        audio.pause();
        playPauseButton.innerHTML = '<i class="bi bi-play-fill"></i>';
        progressBar.disabled = false; // Снова делаем ползунок активным
    }
}

function stopAudio(audioId) {
    let audioContainer = document.getElementById(audioId + "_audioContainer");
    let audio = audioContainer.audio;
    let progressBar = document.getElementById(audioId + "_audio_progress"); // Ползунок прогресса
    if (audio) {
        audio.pause();
        audio.currentTime = 0;
        progressBar.value = 0; // Сбрасываем ползунок прогресса
        document.getElementById(audioId + "_audio_start").innerHTML = '<i class="bi bi-play-fill"></i>'; // Сбрасываем кнопку на воспроизведение
        progressBar.disabled = false; // Делаем ползунок прогресса активным после остановки
    }
}


document.getElementById('toolsPanel').addEventListener('click', function(event) {
    let target = event.target.closest('button'); // Используем closest для улучшения селектора
    if (!target) return; // Выход, если клик не по кнопке
    let audioId = target.id.split('_')[0];

    if (target.classList.contains('startAudio') || target.classList.contains('pauseAudio')) {
        togglePlayPause(audioId);
    } else if (target.classList.contains('stopAudio')) {
        stopAudio(audioId);
    } else if (target.classList.contains('closeAudio')) {
        closeAudioPlayer(audioId);
    }
});


// Функция для закрытия аудиоплеера
function closeAudioPlayer(audioId) {
    let audioContainer = document.getElementById(audioId + "_audioContainer");
    stopAudio(audioId);  // Остановка воспроизведения перед закрытием
    audioContainer.parentNode.removeChild(audioContainer);  // Удаление контейнера
}
