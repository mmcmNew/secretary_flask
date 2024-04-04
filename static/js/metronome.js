// Функция для начала работы метронома
function startMetronome(metronomeId) {
    let metronomeContainer = $("#" + metronomeId + "_metronomeContainer");
    // Проверяем, не запущен ли уже таймер
    if (!metronomeContainer.data('isRunning')) {
        let bpm = parseInt($("#" + metronomeId + "_metronome_range").val());
        let interval = 60000 / bpm; // Вычисляем интервал в миллисекундах
        let tickCount = parseInt($("#" + metronomeId + "_tick_count").val()) || Infinity; // Получаем количество тиков

        var tickAudioUrl = "/static/audio/click1.mp3";
        let audio = new Audio(tickAudioUrl);
        let currentTick = 0; // Текущее количество тиков
        let timer = setInterval(function() {
            if (currentTick < tickCount) {
                audio.play();
                currentTick++;
            } else {
                stopMetronome(metronomeId); // Останавливаем метроном после достижения нужного количества тиков
            }
        }, interval);

        metronomeContainer.data('isRunning', true);
        metronomeContainer.data('timer', timer);
    }
}

// Функция для остановки метронома
function stopMetronome(metronomeId) {
    let metronomeContainer = $("#" + metronomeId + "_metronomeContainer");
    clearInterval(metronomeContainer.data('timer'));
    metronomeContainer.data('isRunning', false);
    metronomeContainer.trigger('metronomeStopped', [metronomeId]);
}

// Функция для обработки изменения BPM
function changeBPM(metronomeId) {
    let metronomeContainer = $("#" + metronomeId + "_metronomeContainer");
    let newBPM = parseInt($("#" + metronomeId + "_metronome_range").val());
    $("#" + metronomeId + "_label").text(newBPM + " bpm");
    if (metronomeContainer.data('isRunning')) {
        stopMetronome(metronomeId);
        startMetronome(metronomeId);
    }
}

// Функция для закрытия метронома
function closeMetronome(metronomeId) {
    let metronomeContainer = $("#" + metronomeId + "_metronomeContainer");
    if (metronomeContainer.data('isRunning')) {
        clearInterval(metronomeContainer.data('timer'));
    }
    metronomeContainer.remove();
    if ($("#toolsPanel").children().length === 0)
        $('#toolsPanel').attr('hidden', true);
}

// Слушатели событий для кнопок и изменения BPM
$(document).ready(function() {
    $('#toolsPanel').on('click', '.startMetronome', function() {
        let metronomeId = this.id.split('_')[0];
        startMetronome(metronomeId);
    });

    $('#toolsPanel').on('click', '.stopMetronome', function() {
        let metronomeId = this.id.split('_')[0];
        stopMetronome(metronomeId);
    });

    $('#toolsPanel').on('click', '.closeMetronome', function() {
        let metronomeId = this.id.split('_')[0];
        closeMetronome(metronomeId);
    });

    $('#toolsPanel').on('input change', '.rangeMetronome', function() {
        let metronomeId = this.id.split('_')[0];
        changeBPM(metronomeId);
    });
});

