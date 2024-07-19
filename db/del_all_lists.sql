--Удаление всех списков

DELETE FROM task_list_relations WHERE ListID IN (SELECT ListID FROM lists);
DELETE FROM list_project_relations WHERE ListID IN (SELECT ListID FROM lists);
DELETE FROM list_group_relations WHERE ListID IN (SELECT ListID FROM lists);

DELETE FROM lists;

-- Сброс автоинкрементного счетчика для таблицы `lists`
UPDATE sqlite_sequence SET seq = 0 WHERE name = 'lists';