from pymongo import MongoClient
import sqlite3

mconn = MongoClient()
db = mconn.simpleTodo

all_todos = db.todos.find({})
all_logs  = db.todo_logs.find({})


conn = sqlite3.connect("simpleTodo.db")
c = conn.cursor()
c.executescript(
"""
--drop table todos;
--drop table todo_logs;
create table if not exists todos(
todo_id integer,
due_date text,
frequency text,
remind_before_days integer,
task_name text,
time_slot integer,
todo_action text,
track_habit integer
);

create table if not exists todo_logs (
todo_id integer,
action text,
due_date text,
creation_timestamp text
);
"""
)

for todo in all_todos:
    #insert
    if 'remindBeforeDays' not in todo:
        todo['remindBeforeDays'] = None
    if 'timeSlot' not in todo:
        todo['timeSlot'] = None
    if 'trackHabit' not in todo:
        todo['trackHabit'] = None
    if 'todo_action' not in todo:
        todo['todo_action'] = None
    if 'due_date' not in todo:
        todo['due_date'] = None
    if todo['due_date']:
        todo_due_date = todo['due_date'].isoformat()
    else:
        todo_due_date = None
    c.execute('insert into todos (todo_id, due_date, frequency, remind_before_days, task_name, time_slot, todo_action, track_habit) values(?,datetime(?),?,?,?,?,?,?)',(todo['todo_id'], todo_due_date, todo['frequency'], todo['remindBeforeDays'], todo['task'], todo['timeSlot'], todo['todo_action'], todo['trackHabit']))

for todo_log in all_logs:
    #insert
    c.execute('insert into todo_logs (todo_id, action, due_date, creation_timestamp) values(?,?,datetime(?),datetime(?))', (todo_log['todo_id'], todo_log['action'], todo_log['due_date'].isoformat(), todo_log['creation_timestamp'].isoformat()))


conn.commit()
conn.close()
