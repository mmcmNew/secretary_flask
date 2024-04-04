function closeMemory(memoryId) {
    let memoryContainer = $("#" + memoryId + "_memoryContainer");
    memoryContainer.remove();
    if ($("#toolsPanel").children().length === 0) {
        $('#toolsPanel').attr('hidden', true);
    }
}

$('#toolsPanel').on('click', '.closeMemory', function() {
    let memoryId = this.id.split('_')[0];
    closeMemory(memoryId);
});


// Функция для отправки запроса
function sendRequest(requestType, params) {
    // AJAX-запрос
    $.ajax({
        url: '/memory', // Укажите ваш URL
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ type: requestType, params: params }),
        success: function(response) {
            // Очистка карусели
            let carouselId = params.memoryId + '_carousel';
            $('#' + carouselId + ' .carousel-inner').empty();
            // Добавление новых карточек
            if(response.cards && response.cards.length) {
                response.cards.forEach(function(card, index) {
                    let isActive = index === 0 ? ' active' : '';
                    let cardHtml = `<div class="carousel-item${isActive}">
                                        <img src="static/images/${card.url}" class="d-block w-100 h-100 carousel-image" alt="${card.text}">
                                    </div>`;
                    $('#' + carouselId + ' .carousel-inner').append(cardHtml);

                    if (index === 0) {
                        $('#' + params.memoryId + '_carouselOverlay').text(card.text);
                    }
                });
            } else {
                console.log("No cards received");
            }

            // Переинициализация карусели
            $('#' + carouselId).carousel('dispose').carousel();
        },
        error: function(xhr, status, error) {
            console.error('Error: ', error);
        }
    });
}

// Обработка кликов на динамически добавляемой кнопке внутри #toolsPanel
$('#toolsPanel').on('click', '[id$=_newSet]', function() {
    // Извлечение идентификатора memory из ID кнопки
    let memoryId = this.id.split('_')[0];
    // Получение количества слов из соответствующего поля ввода
    let wordsCount = $('#' + memoryId + '_wordsCount').val();

    // Подготовка параметров для запроса
    let params = {
        memoryId: memoryId,
        count: wordsCount
    };

    // Вызов функции отправки запроса с типом запроса и параметрами
    sendRequest('references', params);
    $('#' + params.memoryId + '_textModeSwitch').prop('checked', false).trigger('change');
});


// Обработка кликов на динамически добавляемой кнопке внутри #toolsPanel
$('#toolsPanel').on('click', '[id$=_startMemorizing]', function() {
    // Извлечение идентификатора memory из ID кнопки
    let memoryId = this.id.split('_')[0];
    // Получение количества слов из соответствующего поля ввода
    let textInput = $('#' + memoryId + '_textInput')
    let words = textInput.val();
    let delimiter = $('#' + memoryId + '_delimiter').val() || ' ';

    $('#' + memoryId + '_collapse').collapse('hide');

    // Подготовка параметров для запроса
    let params = {
        memoryId: memoryId,
        words: words,
        delimiter: delimiter
    };

    // Вызов функции отправки запроса с типом запроса и параметрами
    sendRequest('words', params);
    $('#' + params.memoryId + '_textModeSwitch').prop('checked', true).trigger('change');
});

$('#toolsPanel').on('click', '[id$=_checkText]', function() {
    let memoryId = this.id.split('_')[0];
    let inputText = $('#' + memoryId + '_textInput').val();
    let resultText = $('#' + memoryId + '_checkTextInput').val();

    // Проверка, что поле ввода результата не пустое
    if (!resultText.trim()) {
        return; // Прерывание функции, если поле пустое
    }

    // Подготовка параметров для запроса
    let requestData = {
        text: inputText,
        userText: resultText
    };

    // AJAX-запрос на сервер для проверки результатов
    $.ajax({
        url: '/check_results', // Укажите ваш URL
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        success: function(response) {
            // Вывод обработанного текста с пометкой неправильных слов и общего результата
            $('#' + memoryId + '_resultContainer').html(response); // предполагаем, что `response` уже содержит размеченную строку
        },
        error: function(xhr, status, error) {
            console.error('Error: ', error);
        }
    });
});