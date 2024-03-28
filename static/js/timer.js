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
    let timerContainer = $("#" + timerId + "_container");
    if (!timerContainer.data('isRunning')) {
        let timeRemaining = getTimeRemaining(timerId);
        if (timeRemaining === 0) {
            resetTimeInputs(timerId);
            timeRemaining = getTimeRemaining(timerId);
        }
        timerContainer.data('timeRemaining', timeRemaining);
        timerContainer.data('timer', setInterval(function() { updateTimer(timerId) }, 1000));
        timerContainer.data('isRunning', true);
    }
}

function stopTimer(timerId) {
    let timerContainer = $("#" + timerId + "_container");
    if (timerContainer.data('isRunning')) {
        clearInterval(timerContainer.data('timer'));
        timerContainer.data('isRunning', false);
    }
}

function resetTimer(timerId) {
    let timerContainer = $("#" + timerId + "_container");
    clearInterval(timerContainer.data('timer'));
    resetTimeInputs(timerId);
    timerContainer.data('isRunning', false);
}

function updateTimer(timerId) {
    let timerContainer = $("#" + timerId + "_container");
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
    $("#" + timerId + "_hours").val('00');
    $("#" + timerId + "_minutes").val('00');
    $("#" + timerId + "_seconds").val('00');
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
    let timerContainer = $("#" + timerId + "_container");
    if (timerContainer.data('isRunning')) {
        clearInterval(timerContainer.data('timer'));
    }
    timerContainer.remove();
    if ($("#toolsPanel").children().length === 0)
        $('#toolsPanel').attr('hidden', true);
}

function playTimerEndSoundAndText(timerId) {
    let timerEndSound = new Audio('/static/audio/timer-sound.mp3');
    timerEndSound.play();
    timerEndSound.onended = function() {
        let text = $("#" + timerId + "_name").val();
        if (text.trim() === '') return
        generateAudioURLFromText(text).then(audioUrl => {
            let audio = new Audio(audioUrl);
            audio.play();
        }).catch(error => {
            console.error("Error generating audio:", error);
        });
    };
}