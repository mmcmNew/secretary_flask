$(document).ready(function() {
    $('#toolsPanel').on('click', '.startTimer', function() {
        let timerId = this.id.split('_')[0];
        startTimer(timerId);
    });

    $('#toolsPanel').on('click', '.stopTimer', function() {
        let timerId = this.id.split('_')[0];
        stopTimer(timerId);
    });

    $('#toolsPanel').on('click', '.resetTimer', function() {
        let timerId = this.id.split('_')[0];
        resetTimer(timerId);
    });

    $('#toolsPanel').on('click', '.closeTimer', function() {
        let timerId = this.id.split('_')[0];
        closeTimer(timerId);
    });
});

function startTimer(timerId) {
    let timerContainer = $("#" + timerId + "_timerContainer");
    if (!timerContainer.data('isRunning')) {
        let timeRemaining = getTimeRemaining(timerId);
        if (timeRemaining === 0) {
            resetTimeInputs(timerId);
            timeRemaining = getTimeRemaining(timerId);
        }

        // Создаем Worker
        let timerWorker = new Worker('static/js/timerWorker.js');
        timerContainer.data('timerWorker', timerWorker);
        timerContainer.data('isRunning', true);

        // Обработка сообщений от Worker
        timerWorker.onmessage = function(e) {
            const { action, timeRemaining } = e.data;
            switch (action) {
                case 'update':
                    displayTime(timerId, timeRemaining);
                    timerContainer.data('timeRemaining', timeRemaining);
                    break;
                case 'end':
                    stopTimer(timerId);
                    playTimerEndSoundAndText(timerId);
                    break;
            }
        };

        // Запуск Worker
        timerWorker.postMessage({ action: 'start', timeRemaining });
    }
}

function stopTimer(timerId) {
    let timerContainer = $("#" + timerId + "_timerContainer");
    let timerWorker = timerContainer.data('timerWorker');
    if (timerWorker) {
        timerWorker.terminate(); // Останавливаем Worker
        timerContainer.removeData('timerWorker');
    }
    timerContainer.data('isRunning', false);
    resetTimeInputs(timerId);
}

function resetTimer(timerId) {
    let timerContainer = $("#" + timerId + "_timerContainer");
    let timerWorker = timerContainer.data('timerWorker');
    if (timerWorker) {
        timerWorker.terminate(); // Останавливаем и удаляем Worker
        timerContainer.removeData('timerWorker');
    }
    resetTimeInputs(timerId); // Сброс визуального отображения таймера
    timerContainer.data('isRunning', false);
    // Удаляем оставшееся время из данных, если есть
    timerContainer.removeData('timeRemaining');
}


function updateTimer(timerId) {
    let timerContainer = $("#" + timerId + "_timerContainer");
    let timeRemaining = timerContainer.data('timeRemaining') - 1000;
    timerContainer.data('timeRemaining', timeRemaining);
    resetTimeInputs(timerId)

    if (timeRemaining <= 0) {
        clearInterval(timerContainer.data('timer'));
        timerContainer.data('isRunning', false);
        playTimerEndSoundAndText(timerId);
    } else {
        displayTime(timerId, timeRemaining);
    }
}

function getTimeRemaining(timerId) {
    return parseInt($("#" + timerId + "_hours").val() || 0) * 3600000 +
           parseInt($("#" + timerId + "_minutes").val() || 0) * 60000 +
           parseInt($("#" + timerId + "_seconds").val() || 0) * 1000;
}

function resetTimeInputs(timerId) {
    $("#" + timerId + "_hours").val('');
    $("#" + timerId + "_minutes").val('');
    $("#" + timerId + "_seconds").val('');
}

function displayTime(timerId, timeRemaining) {
    let hours = Math.floor(timeRemaining / 3600000);
    let minutes = Math.floor((timeRemaining % 3600000) / 60000);
    let seconds = Math.floor((timeRemaining % 60000) / 1000);

    $("#" + timerId + "_hours").val(formatTime(hours));
    $("#" + timerId + "_minutes").val(formatTime(minutes));
    $("#" + timerId + "_seconds").val(formatTime(seconds));
}

function formatTime(time) {
    return time < 10 ? '0' + time : time;
}

function closeTimer(timerId) {
    let timerContainer = $("#" + timerId + "_timerContainer");
    let timerWorker = timerContainer.data('timerWorker');
    if (timerWorker) {
        timerWorker.terminate(); // Останавливаем и удаляем Worker
        timerContainer.removeData('timerWorker');
    }
    timerContainer.remove(); // Удаление контейнера таймера из DOM
    if ($("#toolsPanel").children().length === 0) {
        $('#toolsPanel').attr('hidden', true); // Скрываем панель инструментов, если таймеров больше нет
    }
}

function playTimerEndSoundAndText(timerId) {
    let timerContainer = $("#" + timerId + "_timerContainer");
    let timerEndSound = new Audio('/static/audio/timer-sound.mp3');
    let fullTimerId = timerId //+ '_timerContainer'
    timerEndSound.play();
    timerEndSound.onended = function() {
        let text = $("#" + timerId + "_input").val();
        if (text.trim() !== '') {
            generateAudioURLFromText(text).then(audioUrl => {
                let audio = new Audio(audioUrl);
                audio.play();
                audio.onended = function() {
                    // Теперь здесь вызываем trigger для 'timerStopped'
                    // console.log(timerContainer)
                    timerContainer.trigger('timerStopped', [fullTimerId]);
                };
            }).catch(error => {
                console.error("Error generating audio:", error);
                // Не забудьте вызвать trigger даже в случае ошибки
                timerContainer.trigger('timerStopped', [fullTimerId]);
            });
        } else {
            // Если текста нет, сразу вызываем trigger для 'timerStopped'
            timerContainer.trigger('timerStopped', [fullTimerId]);
        }
    };
}