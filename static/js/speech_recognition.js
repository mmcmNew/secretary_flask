// Проверяем, поддерживается ли API в браузере
window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (window.SpeechRecognition) {
    var recognition = new SpeechRecognition();
    recognition.lang = 'ru-RU'; // Установите нужный язык
    recognition.interimResults = true; // Установите true, если хотите видеть промежуточные результаты

    recognition.onresult = function(event) {
        var transcript = Array.from(event.results)
            .map(result => result[0])
            .map(result => result.transcript)
            .join('');

        // Проверка на наличие слов "стоп" или "отменить"
        if (transcript.toLowerCase().includes("стоп") || transcript.toLowerCase().includes("отменить")) {
            recognition.stop();  // Прекращаем распознавание
            console.log("Распознавание прервано по команде пользователя.");
        } else if (event.results[0].isFinal) {  // Проверка, является ли результат окончательным
            sendMessage(transcript);
        }
    };

    $('#start-recognition').click(function() {
        recognition.start();
    });
} else {
    console.log("Ваш браузер не поддерживает Web Speech API");
}
