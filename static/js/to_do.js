$(document).ready(function() {
    $('.to-do').click(function () {
        let buttonId = this.id;  // Получаем ID кнопки
        let objectName = $('#input-group-name').val(); // Получаем имя объекта
        //прерываем если имени объекта нет
        if (!objectName) {
            return;
        }

        let objectType = buttonId.split('_')[1];  // Определяем тип объекта: list, group
        $('#input-group_name').val(''); // Очищаем поле ввода имени объекта

        if (objectName) {
            $.post('/add_list', {name: objectName, type: objectType}, function (response) {
                if (response.success) {
                    $.get('/get_groups', function (data) {
                        $('#groupsContainer').html(data.html);
                    });
                } else {
                    alert('Ошибка: ' + response.message);
                }
            });
        }
    });

    $('#button-add-task').click(function () {
        let taskTitle = $('#input-task-title').val(); // Получаем название задачи
        //проверяем что имя не пустое
        if (!taskTitle) {
            return;
        }
        $('#input-task-title').val(''); // Очищаем поле ввода
        let listFullId = $('#groupsContainer .list-group-item.active').attr('id'); // Получаем ID активного списка
        let listId = $('#groupsContainer .list-group-item.active').attr('id').split('_')[0] || 'tasks';

        if (taskTitle) {
            $.post('/add_task', {title: taskTitle, list_id: listId}, function (response) {
                if (response.success) {
                    $.get('/get_groups', function (data) {
                        $('#groupsContainer').html(data.html);
                        $('#' + listFullId).click(); // Инициируем клик по элементу
                        $('#' + listFullId).addClass('active'); // Добавляем класс 'active' // Активируем элемент после загрузки данных
                    });
                } else {
                    alert('Ошибка: ' + response.message);
                }
            });
        }
    });

    // Добавляем обработчик кликов на родительский контейнер всех списков
    $('#groupsContainer').on('click', '.list-group-item', function () {
        // Убираем класс 'active' у всех элементов списка
        $('#groupsContainer .list-group-item').removeClass('active');
        // Добавляем класс 'active' к элементу, по которому был произведен клик
        $(this).addClass('active');

        // Загрузка данных или выполнение других действий
        let listId = $(this).attr('id').split('_')[0];
        $.get('/get_tasks', {list_id: listId}, function (data) {
            $('#tasksContainer').html(data.html);
        });
    });


    // Добавляем обработчик кликов на родительский контейнер всех списков
    $('#tasksContainer').on('click', '.list-group-item', function () {
        // Убираем класс 'active' у всех элементов списка
        $('#tasksContainer .list-group-item').removeClass('active');
        // Добавляем класс 'active' к элементу, по которому был произведен клик
        $(this).addClass('active');

        let taskId = $(this).attr('id').split('_')[0];
        $.get('/get_tasks_edit', {task_id: taskId}, function (data) {
            $('#editContainer').html(data.html);
        });
    });

    $('#editContainer').on('click', '#button-add-subtask', function () {
        let subTaskTitle = $('#input-subtask-title').val(); // Получаем название задачи
        if (!subTaskTitle) {
            return;
        }
        $('#input-subtask-title').val(''); // Очищаем поле ввода
        let taskId = $('#button-add-subtask').attr('name');
        //получить id нажатого элемента
        let taskElement = $('#tasksContainer .list-group-item.active');
        //получить id родительского элемента
        taskElementId = taskElement.attr('id').replace('_task', '');
        let taskDiv = $('#' + taskElementId + '_taskDiv');

        $.post('/add_task', {title: subTaskTitle, task_id: taskId}, function (response) {
            if (response.success) {
                let newTaskElement = $(response.div);
                taskDiv.replaceWith(newTaskElement)
                taskElement = $('#' + newTaskElement.attr('id').replace('Div', ''));
                taskElement.click(); // Инициируем клик по элементу
                taskElement.addClass('active'); // Добавляем класс 'active'
                // для каждого элемента с name taskId внутри контейнера tasksContainer заменить на response.div
                $('#tasksContainer').each(function () {
                    if ($(this).attr('name') === taskId) {
                        $(this).replaceWith(newTaskElement);
                    }
                });
            }
        });

    });
});




