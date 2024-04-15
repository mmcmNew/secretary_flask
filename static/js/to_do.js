$(document).ready(function() {
    $('.to-do').click(function () {
        let buttonId = this.id;  // Получаем ID кнопки
        let objectName = $('#input-group-name').val(); // Получаем имя объекта
        let objectType = buttonId.split('_')[1];  // Определяем тип объекта: list, group, task
        $('#input-group_name').val(''); // Очищаем поле ввода имени объекта

        if (objectName) {
            $.post('/add_object', {name: objectName, type: objectType}, function (response) {
                if (response.success) {
                    $.get('/get_groups', function(data) {
                        $('#groupsContainer').html(data.html);
                    });
                    initEventListeners();
                } else {
                    alert('Ошибка: ' + response.message);
                }
            });
        }
    });

    $('#button-add-task').click(function () {
        let taskTitle = $('#input-task-title').val(); // Получаем название задачи
        $('#input-task-title').val(''); // Очищаем поле ввода
        // ID списка по активному элементу в groupsContainer
        let list_id = $('.list-group-link.active').data('id') || 'default';

        if (taskTitle) {
            $.post('/add_task', {title: taskTitle, list_id: list_id}, function (response) {
                if (response.success) {
                    $.get('/get_tasks', {list_id: list_id}, function(data) { // Передаём list_id
                        $('#tasksContainer').html(data.html);
                        initEventListeners();  // Обновление слушателей после изменения DOM
                    });
                } else {
                    alert('Ошибка: ' + response.message);
                }
            });
        }
    });
});



document.addEventListener('DOMContentLoaded', function() {
    var links = document.querySelectorAll('.list-group-link');
    links.forEach(link => {
        link.addEventListener('click', function() {
            links.forEach(lnk => lnk.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var listItems = document.querySelectorAll('.task-item');
    listItems.forEach(function(item) {
        item.addEventListener('click', function() {
            listItems.forEach(function(innerItem) {
                innerItem.classList.remove('active');
            });
            this.classList.add('active');
        });
    });
});


// Функция инициализации выбранных элементов после обновления содержимого
function initEventListeners() {
    var links = document.querySelectorAll('.list-group-link');
    links.forEach(link => {
        link.addEventListener('click', function() {
            links.forEach(lnk => lnk.classList.remove('active'));
            this.classList.add('active');
        });
    });

    var listItems = document.querySelectorAll('.task-item');
    listItems.forEach(function(item) {
        item.addEventListener('click', function() {
            listItems.forEach(function(innerItem) {
                innerItem.classList.remove('active');
            });
            this.classList.add('active');
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initEventListeners(); // Инициализируем слушателей при загрузке страницы
});


