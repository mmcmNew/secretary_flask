$(document).ready(function() {
    function scrollToBottom() {
        var chat = $("#chat");
        chat.animate({ scrollTop: chat.prop("scrollHeight") }, "slow");
    }

    $('#sendMessage').click(function() {
        sendMessage();
    });

    $(document).ready(function() {
        $('.quick-command').on('click', function() {
            var commandId = $(this).data('command-id');
            sendMessage(commandId);
        });
    });

    function sendMessage(customMessage) {
        var isCustomMessage = false;
        if (customMessage) {
            var isCustomMessage = true;
        }
        var message = customMessage || $('#message-area').val();
        if ($.trim(message) === '') {
            return; // Прерываем функцию, чтобы не отправлять запрос
        }
        $.ajax({
            type: 'POST',
            url: '/new-message',
            data: { 'message': message },
            success: function(data) {
                $('#chat').append(data.div);
                if (!isCustomMessage) {
                    $('#message-area').val(''); // Очищаем только если сообщение взято из поля ввода
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

    //Прокрутка чата при открытии
    scrollToBottom();

});