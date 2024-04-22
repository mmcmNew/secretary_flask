function addGroupAndList (objectType, objectName) {
    // прроверка наличия обоих переменных
    if (!objectType || !objectName) {
        return;
    }
    // отправка запроса на сервер
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

// добавляем задачу и обновляем элемент списка
function addTask(taskTitle, activeList = $('#tasks')) {
    // Проверка на наличие названия задачи
    if (!taskTitle) {
        return;
    }

    let listId = activeList.data('list-id');
    // Отправка запроса на сервер
    $.post('/add_task', {title: taskTitle, list_id: listId}, function (response) {
        if (response.success) {
            // Получение и обновление списка задач
            $.post('/update_list', {list_id: listId}, function (data) {
                let newTasksList = $(data.html);
                activeList.replaceWith(newTasksList);
                newTasksList.click(); // Инициируем клик по новому элементу для обновления списка задач
                newTasksList.addClass('active'); // Добавляем класс 'active' новому элементу
            });
        } else {
            alert('Ошибка: ' + response.message);
        }
    });
}

//получаем область редактирования задачи
function getTaskEdit(taskId, taskDivId) {
    $.get('/get_tasks_edit', {taskId: taskId, taskDivId: taskDivId}, function (data) {
        if (data.status) {
            $('#editContainer').html(data.html);
        } else {
            alert('Ошибка получения данных задачи');
        }
    });
}

function addSubtask(taskId, subtaskTitle, taskDivId) {
    $.post('/add_subtask', {title: subtaskTitle, task_id: taskId}, function (response) {
        if (response.success) {
            let taskDiv = $('#' + taskDivId + '_taskDiv');
            let newTaskElement = $(response.div);
            taskDiv.replaceWith(newTaskElement)
            // находим элемент с классом 'list-group-item' внутри newTaskElement и кликаем по нему
            let taskElement = newTaskElement.find('.list-group-item').first();
            taskElement.click();
            taskElement.addClass('active');
            // т.к. подзадача может повторяться в разных задачах то обновляем все задчи с этой подзадачей
            // $('#tasksContainer').each(function () {
            //    if ($(this).data('task-id') === taskId) {
                    // добавляем к id нового элемента случайное число
            //        let randomNumber = Math.floor(Math.random() * 1000000);
            //        newTaskElement.attr('id', randomNumber);
            //        $(this).replaceWith(newTaskElement);
            //    }
            //});
        }
    });
}


function taskStatusUpdate(taskId, isChecked, taskDivId) {
    $.ajax({
            url: '/update_task',
            type: 'POST',
            data: {
                task_id: taskId,
                task_status: isChecked
            },
            success: function (response) {
                if (isChecked) {
                    var tickAudioUrl = "/static/audio/isComplited.wav";
                    let audio = new Audio(tickAudioUrl);
                    audio.play();
                }
            },
            error: function (xhr, status, error) {
                // Обработка ошибки
                console.error('Error updating task status:', error);
            }
        });
}

$(document).ready(function() {
    $('.to-do').click(function () {
        let buttonId = this.id;  // Получаем ID кнопки
        let objectName = $('#input-group-name').val(); // Получаем имя объекта

        let objectType = buttonId.split('_')[1];  // Определяем тип объекта: list, group
        $('#input-group_name').val(''); // Очищаем поле ввода имени объекта

        addGroupAndList(objectType, objectName);
    });

    $('#button-add-task').click(function () {
        let taskTitle = $('#input-task-title').val(); // Получаем название задачи
        //проверяем что имя не пустое
        if (!taskTitle) {
            return;
        }
        $('#input-task-title').val(''); // Очищаем поле ввода
        let activeList = $('#groupsContainer .list-group-item.active') || None;
        addTask(taskTitle, activeList);
    });

    // Клик по списку
    $('#groupsContainer').on('click', '.list-group-item', function () {
        // Убираем класс 'active' у всех элементов списка
        $('#groupsContainer .list-group-item').removeClass('active');
        // Добавляем класс 'active' к элементу, по которому был произведен клик
        $(this).addClass('active');

        // Загрузка данных или выполнение других действий
        let listId = $(this).data('list-id');
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
        let taskDivId = $(this).data('parent-id');
        let taskId = $(this).data('task-id');
        getTaskEdit(taskId, taskDivId);
    });

    // привязываем обработчик клика к родительскому контейнеру потому что контейнер динамически обновляется
    $('#editContainer').on('click', '#button-add-subtask', function () {
        let subtaskTitle = $('#input-subtask-title').val(); // Получаем название задачи
        if (!subtaskTitle) {
            return;
        }
        $('#input-subtask-title').val(''); // Очищаем поле ввода
        let taskId = $('#button-add-subtask').data('task-id');
        //получить id родительского элемента в списке задач
        taskDivID = $('#button-add-subtask').data('parent-id');

        addSubtask(taskId, subtaskTitle, taskDivID);
    });

    // Задача выполнена
    $('#tasksContainer').on('change', 'input[type="checkbox"]', function() {

        const taskId = $(this).data('task-id');
        const taskDivId = $(this).data('parent-id');
        const isChecked = $(this).is(':checked');

        // установка галочек для всех подзадач внутри taskDiv
        const taskDiv = $('#' + taskDivId + '_taskDiv');
        if (isChecked) {
            taskDiv.find('input[type="checkbox"]').prop('checked', isChecked);
            taskDiv.find('label').addClass('text-decoration-line-through');
        } else {
            // удаляет класс text-decoration-line-through (зачеркивание)
            taskDiv.find('.text-decoration-line-through').first().removeClass('text-decoration-line-through');
        }

        taskStatusUpdate(taskId, isChecked, taskDivId);

        // найти ближайший элемент списка и кликнуть по нему
        let taskElement = taskDiv.find('.list-group-item').first();
        taskElement.click();
        taskElement.addClass('active');

    });

    $('#editContainer').on('change', 'input[type="checkbox"]', function() {

        const taskId = $(this).data('task-id');
        const taskDivId = $(this).data('parent-id');
        const isChecked = $(this).is(':checked');

        taskStatusUpdate(taskId, isChecked, taskDivId);

        let taskDiv = $('#' + taskDivId + '_taskDiv');
        // найти в taskDivId элементы с data-task-id равным taskId и изменить галочку
        taskDiv.find('input[type="checkbox"]').each(function() {
            if ($(this).data('task-id') === taskId) {
                $(this).prop('checked', isChecked);
                if (isChecked) {
                    // найти ближайший label и добавить класс text-decoration-line-through
                    let label = $(this).next('label');
                    label.addClass('text-decoration-line-through');
                }
                else {
                    let label = $(this).next('label');
                    label.removeClass('text-decoration-line-through');
                }
            }
        });
    });

});
