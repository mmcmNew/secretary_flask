function scrollToBottom() {
    var chat = $("#chat");
    chat.animate({ scrollTop: chat.prop("scrollHeight") }, "slow");
}

$('#sendMessage').click(function() {
    sendMessage();
});


$('.quick-command').on('click', function() {
    var commandId = $(this).data('command-id');
    sendMessage(commandId);
});


function sendMessage(customMessage, message_type) {
    // в начале определяем это сообщение по нажатию кнопки или запрос нет
    // если нет то значит нужно получить ответ от обработчика команд
    var message = customMessage || $('#message-area').val();
    if ($.trim(message) === '') {
        return;
    }
    $('#sendMessage').html('<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> <span class="visually-hidden" role="status">Loading...</span>').attr('disabled', true);
    if (!message_type) {
         message_type = 'request'
    }

    $.ajax({
        type: 'POST',
        url: '/new-message',
        contentType: 'application/x-www-form-urlencoded',
        data: { 'message': message, 'type': message_type },
        success: function(data) {
            $('#chat').append(data.div);
            if (data.type === 'request') {
                $('#message-area').val(''); // Очищаем только если сообщение взято из поля ввода
                sendMessage(message, 'answer')
            }
            else {
                $('#sendMessage').html('Send').attr('disabled', false);
            }
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