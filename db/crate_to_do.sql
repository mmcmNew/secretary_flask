BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "list_project_relations" (
	"ListID"	INT,
	"ProjectID"	INT,
	PRIMARY KEY("ListID","ProjectID"),
	FOREIGN KEY("ProjectID") REFERENCES "projects"("ProjectID"),
	FOREIGN KEY("ListID") REFERENCES "lists"("ListID") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "list_group_relations" (
	"ListID"	INT,
	"GroupID"	INT,
	PRIMARY KEY("ListID","GroupID"),
	FOREIGN KEY("GroupID") REFERENCES "groups"("GroupID") ON DELETE CASCADE,
	FOREIGN KEY("ListID") REFERENCES "lists"("ListID")
);
CREATE TABLE IF NOT EXISTS "task_list_relations" (
	"TaskID"	INT,
	"ListID"	INT,
	PRIMARY KEY("TaskID","ListID"),
	FOREIGN KEY("TaskID") REFERENCES "tasks"("TaskID"),
	FOREIGN KEY("ListID") REFERENCES "lists"("ListID") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "task_project_relations" (
	"TaskID"	INT,
	"ProjectID"	INT,
	PRIMARY KEY("TaskID","ProjectID"),
	FOREIGN KEY("TaskID") REFERENCES "tasks"("TaskID") ON DELETE CASCADE,
	FOREIGN KEY("ProjectID") REFERENCES "projects"("ProjectID") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "lists" (
	"ListID"	INTEGER UNIQUE,
	"ListName"	VARCHAR(255),
	PRIMARY KEY("ListID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "groups" (
	"GroupID"	INTEGER UNIQUE,
	"GroupName"	VARCHAR(255),
	PRIMARY KEY("GroupID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "intervals" (
	"IntervalID"	INTEGER UNIQUE,
	"IntervalMinutes"	INT,
	PRIMARY KEY("IntervalID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "priorities" (
	"PriorityID"	INTEGER UNIQUE,
	"PriorityName"	VARCHAR(255),
	PRIMARY KEY("PriorityID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "projects" (
	"ProjectID"	INTEGER UNIQUE,
	"ProjectName"	VARCHAR(255),
	PRIMARY KEY("ProjectID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "statuses" (
	"StatusID"	INTEGER UNIQUE,
	"StatusName"	VARCHAR(255),
	PRIMARY KEY("StatusID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "task_subtasks_relations" (
	"TaskID"	INT,
	"SubtaskID"	INT,
	PRIMARY KEY("TaskID","SubtaskID"),
	FOREIGN KEY("SubtaskID") REFERENCES "tasks"("TaskID") ON DELETE CASCADE,
	FOREIGN KEY("TaskID") REFERENCES "tasks"("TaskID") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "tasks" (
	"TaskID"	INTEGER UNIQUE,
	"Title"	VARCHAR(255),
	"Description"	TEXT,
	"Deadline"	DATETIME,
	"StatusID"	INT DEFAULT 1,
	"PriorityID"	INT DEFAULT 1,
	"IntervalID"	INT DEFAULT 1,
	"type"	TEXT,
	"Attachments"	TEXT,
	"Note"	TEXT,
	PRIMARY KEY("TaskID" AUTOINCREMENT),
	FOREIGN KEY("PriorityID") REFERENCES "priorities"("PriorityID"),
	FOREIGN KEY("StatusID") REFERENCES "statuses"("StatusID"),
	FOREIGN KEY("IntervalID") REFERENCES "intervals"("IntervalID")
);
COMMIT;
