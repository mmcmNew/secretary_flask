function clearFileList() {
    selectedFiles = []; // Очищаем массив выбранных файлов
    $('#fileList').empty(); // Удаляем все элементы списка файлов на странице
    $('#fileListContainer').hide(); // Скрываем контейнер списка файлов, если он пуст
}

function checkIfListIsEmpty() {
    if ($('#fileList li').length === 0) {
        $('#fileListContainer').hide(); // Скрыть, если список пуст
    }
}

var selectedFiles = []; // Массив для хранения выбранных файлов

$('#fileInput').on('change', function() {
    $.each(this.files, function(i, file) {
        // Проверяем, нет ли файла уже в массиве
        if (selectedFiles.indexOf(file) === -1) {
            selectedFiles.push(file); // Добавляем файл в массив

            // Добавляем файл в список на странице
            var fileEntry = $('<li>').text(file.name);
            var removeButton = $('<button>').text('Удалить').click(function() {
                // Удаляем файл из массива и из списка на странице
                var index = selectedFiles.indexOf(file);
                if (index > -1) {
                    selectedFiles.splice(index, 1);
                }
                $(this).parent().remove();
                checkIfListIsEmpty();
            });
            fileEntry.append(removeButton);
            $('#fileList').append(fileEntry);
        }
    });

    $('#fileListContainer').show();
    checkIfListIsEmpty();
    $('#fileInput').val(''); // Очищаем выбор файлов
});