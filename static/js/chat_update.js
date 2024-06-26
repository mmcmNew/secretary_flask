function scrollToBottom() {
    var chat = $("#chat");
    chat.animate({ scrollTop: chat.prop("scrollHeight") }, "slow");
}

$('#sendMessage').click(function() {
    var messageArea = $('#message-area');
    if ($.trim(messageArea.val()) === '') {
        messageArea.addClass('focus-ring focus-ring-danger'); // Добавляем классы
        messageArea.focus();
    } else {
        sendMessage();
    }
});

$('#message-area').click(function() {
    $(this).removeClass('focus-ring focus-ring-warning'); // Удаляем классы при фокусе
});

$('.quick-command').on('click', function() {
    var commandId = $(this).data('command-id');
    sendMessage(commandId);
});


async function sendMessage(customMessage, message_type) {
    // в начале определяем это сообщение по нажатию кнопки или запрос нет
    // если нет то значит нужно получить ответ от обработчика команд
    var message = customMessage || $('#message-area').val();
    if ($.trim(message) === '') {
        return;
    }
    $('#start-recognition').attr('disabled', true);
    $('#sendMessage').html('<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> <span class="visually-hidden" role="status">Loading...</span>').attr('disabled', true);
    if (!message_type) {
         message_type = 'request'
    }
    var formData = new FormData();
    formData.append('message', message);
    formData.append('type', message_type);
    if (message_type !== 'request') {
        $.each(selectedFiles, function(i, file) { //собираем файлы
            formData.append('file' + i, file);
        });
        clearFileList();
    }

    $.ajax({
        type: 'POST',
        url: '/new-message',
        contentType: false, // Необходимо для правильной работы FormData
        processData: false, // Необходимо для предотвращения преобразования данных в строку
        data: formData, //отправляем сообщение пользователя на сервер
        success: async function(data) {
            $('#chat').append(data.div); //из полученного ответа добавляем div в чат
            if (data.type === 'request') { //если прошлое сообщение было запросом, то повторно отправляем его что получить ответ секретаря
                $('#message-area').val(''); // Очищаем только если сообщение взято из поля ввода
                sendMessage(message, 'answer') //отправляем с меткой чтоб получить ответ, а не только обработку
            }
            if (data.type !== 'request') {
                var lastMessageText = $('#chat').children().last().find('.chat-message-text').text();
                var playButton = $('#chat').children().last().find('.play-audio-button');
                var progressBar = $('#chat').children().last().find('.audio-progress')[0];
                scrollToBottom();
                if (data.type !== 'action_module')
                    playAudioWithPromise(playButton);
            }
            if (data.type === 'component') {
                $('#toolsPanel').attr('hidden', false);
                $('#toolsPanel').append(data.component.div);
                let componentId = data.component.id;
                $('#' + componentId + '_start').click();
            }

            else if (data.type === 'action_module') {
                $('#toolsPanel').attr('hidden', false);
                $('#toolsPanel').append(data.action_module_div.div);
                let action_moduleId = data.action_module_div.id;
                await playAudioWithPromise(playButton);
                processAccordion(action_moduleId);
            }

            else if (data.type === 'memory') {
                $('#toolsPanel').attr('hidden', false);
                $('#toolsPanel').append(data.memory_div.div);
                let memory_moduleId = data.memory_div.id;
                restartCarousel(memory_moduleId);
            }

            $('#start-recognition').attr('disabled', false);
            $('#sendMessage').html('Send').attr('disabled', false); //после получения обработки разблокируем кнопку
            scrollToBottom();
        }
    });
}


$('#message-area').keypress(function(e) {
    if(e.which == 13 && !e.shiftKey) { // 13 это код клавиши Enter, проверяем, что Shift не нажат
        e.preventDefault(); // Предотвращаем стандартное поведение при нажатии Enter (например, перенос строки)
        $('#sendMessage').click(); // Программно вызываем событие click для кнопки отправки
    }
});


$(document).ready(function() {
    //Прокрутка чата при открытии
    scrollToBottom();
})


function playAudioWithPromise(component) {
    return new Promise(resolve => {
        const $component = $(component);
        if ($component) {
            $component.click();
            $component.on('audioTextEnded', () => resolve());
        } else {
            resolve();
        }
    });
}