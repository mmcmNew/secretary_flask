$(document).ready(function(){
    var timer;
    var isTimerRunning = false;

    function getTimeRemaining() {
        return parseInt($("#timerHours").val() || 0) * 3600000 +
               parseInt($("#timerMinutes").val() || 0) * 60000 +
               parseInt($("#timerSeconds").val() || 0) * 1000;
    }

    function updateDisplay(timeRemaining) {
        var hours = Math.floor(timeRemaining / 3600000);
        var mins = Math.floor((timeRemaining % 3600000) / 60000);
        var secs = Math.floor((timeRemaining % 60000) / 1000);

        $("#timerHours").val(formatTime(hours));
        $("#timerMinutes").val(formatTime(mins));
        $("#timerSeconds").val(formatTime(secs));
    }

    function formatTime(time) {
        return time < 10 ? '0' + time : time;
    }

    function updateTimer() {
        var timeRemaining = getTimeRemaining();
        if (timeRemaining <= 0) {
            clearInterval(timer);
            isTimerRunning = false;
            document.getElementById('timerSound').play();
        } else {
            updateDisplay(timeRemaining - 1000);
        }
    }

    $("#startTimer").click(function() {
        if (getTimeRemaining() === 0) return;
        if (!isTimerRunning) {
            timer = setInterval(updateTimer, 1000);
            isTimerRunning = true;
        }
    });

    $("#stop").click(function() {
        if (isTimerRunning) {
            clearInterval(timer);
            isTimerRunning = false;
        }
    });

    $("#reset").click(function() {
        clearInterval(timer);
        $("#timerHours").val('00');
        $("#timerMinutes").val('00');
        $("#timerSeconds").val('00');
        isTimerRunning = false;
    });
});
