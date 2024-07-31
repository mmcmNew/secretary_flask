--Удаление всех задач

DELETE FROM task_list_relations WHERE TaskID IN (SELECT TaskID FROM tasks);
DELETE FROM task_project_relations WHERE TaskID IN (SELECT TaskID FROM tasks);
DELETE FROM task_subtasks_relations WHERE TaskID IN (SELECT TaskID FROM tasks);

DELETE FROM tasks;

-- Сброс автоинкрементного счетчика для таблицы `tasks`
UPDATE sqlite_sequence SET seq = 0 WHERE name = 'tasks';