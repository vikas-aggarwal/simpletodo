import sys
from datetime import datetime
import sqlite3
from TodoTypes import Todo
from TodoTypes import TodoUpdatePayload
from TodoTypes import TodoLogDB

class SimpleTodoDataAccessSqlite3:
    TODO_SELECT_COLUMN_STRING = "todo_id, due_date as 'due_date [timestamp]', frequency, remind_before_days, task_name, time_slot, todo_action, track_habit"
    def __init__(self, APP):
        self.db_path = APP.config['SQLITE3_DB_PATH']
        self.detect_types = sqlite3.PARSE_COLNAMES

        #Create schema is does not exists
        conn = self._getConnection();
        conn.execute('''
        CREATE TABLE if not exists todos(
        todo_id integer,
        due_date text,
        frequency text,
        remind_before_days integer,
        task_name text,
        time_slot integer,
        todo_action text,
        track_habit integer
        )
        ''')

        conn.execute('''
        CREATE TABLE if not exists todo_logs (
        todo_id integer,
        action text,
        due_date text,
        creation_timestamp text
        )
        ''')
        conn.close()
        
    def _getConnection(self):
        conn = sqlite3.connect(self.db_path, detect_types = self.detect_types)
        conn.row_factory = sqlite3.Row
        return conn
        
    def _getTodoObjectFromRow(self, row):

        if row == None:
            return None
        
        todo = {"todo_id": row['todo_id'],
                    "due_date": row['due_date'],
                    "frequency": row['frequency'],
                    "task": row['task_name'],
                    "timeSlot": row['time_slot'],
                    "trackHabit": (row['track_habit'] == 1),
                    "remindBeforeDays": row['remind_before_days']
            } #type: Todo
        return todo

    def _getTodoLogObjectFromRow(self, row):
        todo_log = {"todo_id": row['todo_id'], "action":row['action'], "count" : row['count']} #type: TodoLog
        return todo_log
    
    def get_todo_logs_count(self):
        conn = self._getConnection()
        db = conn.cursor()
        db.execute("select count(*) as count,todo_id,action from todo_logs group by todo_id,action")
        data=[]
        rows = db.fetchall()
        for row in rows:
            data.append(self._getTodoLogObjectFromRow(row))
        return data


    def get_all_todos_by_due_date(self):
        conn = self._getConnection()
        db = conn.cursor()
        db.execute("select "+ self.TODO_SELECT_COLUMN_STRING +" from todos order by datetime(due_date)")
        data = []
        rows = db.fetchall()
        for row in rows:
            todo = self._getTodoObjectFromRow(row) #type: Todo
            data.append(todo)
        return data


    def get_todo(self, todo_id):
        conn = self._getConnection()
        db = conn.cursor()
        db.execute("select "+self.TODO_SELECT_COLUMN_STRING+" from todos where todo_id = ?", (todo_id,))
        row = db.fetchone()
        return self._getTodoObjectFromRow(row)

    def create_todo(self, data, todo_id=None):
        conn = self._getConnection()
        db = conn.cursor()
        if 'due_date' in data:
            data['due_date'] = datetime.utcfromtimestamp(data['due_date'])
        else:
            data['due_date'] = None;

        data['remindBeforeDays'] = data.get('remindBeforeDays')
        data['timeSlot'] = data.get('timeSlot')
        data['trackHabit'] = data.get('trackHabit')
        
        if todo_id == None:
            db.execute("insert into todos (todo_id, due_date, frequency, remind_before_days, task_name, time_slot, todo_action, track_habit) values ((select coalesce(max(todo_id),count(*))+1 from todos), :due_date, :frequency, :remindBeforeDays, :task, :timeSlot, NULL, :trackHabit )",data)
            last_row_id = db.lastrowid
            db.execute("select todo_id from todos where rowid = ?", (last_row_id,))
            row = db.fetchone()
            data["todo_id"] = row["todo_id"]
        else:
            data["todo_id"] = todo_id
            db.execute("insert into todos (todo_id, due_date, frequency, remind_before_days, task_name, time_slot, todo_action, track_habit) values (:todo_id, :due_date, :frequency, :remindBeforeDays, :task, :timeSlot, NULL, :trackHabit )",data)
        conn.commit()
        conn.close()


    def delete_todo(self, todo_id):
        conn = self._getConnection()
        db = conn.cursor()
        db.execute("delete from todos where todo_id = ?", (todo_id,))
        db.execute("delete from todo_logs where todo_id = ?", (todo_id,))
        conn.commit()
        conn.close()

    def upsert_todo(self, todo_id, data #type: TodoUpdatePayload
    ):
        #Getting current state
        todo_object = self.get_todo(todo_id) #type: Todo

        if todo_object == None: #insert
            self.create_todo(data, todo_id)
            return

        conn = self._getConnection()
        db = conn.cursor()

        if 'due_date' in data:
            data['due_date_utc'] = datetime.utcfromtimestamp(data['due_date'])
        else:
            data['due_date_utc'] = todo_object['due_date']


        if "trackHabit" not in data:
            data['trackHabit'] =  todo_object['trackHabit']
            
        data['todo_id'] = todo_id
        data['todo_action'] = data.get("todo_action")

        #get remaining data from payload or existing object
        data['frequency'] = data.get('frequency') or todo_object['frequency']
        data['task'] = data.get('task') or todo_object['task']
        data['timeSlot'] = data.get('timeSlot') or todo_object['timeSlot']
        data['remindBeforeDays'] = data.get('remindBeforeDays') or todo_object['remindBeforeDays']
        db.execute("update todos set due_date=:due_date_utc, frequency=:frequency, remind_before_days=:remindBeforeDays, task_name=:task, time_slot=:timeSlot, track_habit=:trackHabit, todo_action=:todo_action where todo_id = :todo_id", data)
        conn.commit()

        #Delete todo logs if no longer tracked as Habit
        if (('trackHabit' in todo_object) and
                todo_object['trackHabit'] and
                ('trackHabit' in data) and (not data['trackHabit'])):
            db.execute("delete from todo_logs where todo_id = ?", (todo_id,))
            conn.commit()
            conn.close()
            return

        #if obtained via an action log it
        if ('trackHabit' in todo_object) and todo_object['trackHabit'] and ('todo_action' in data):
            todo_log = {
                'action' : data['todo_action'],
                'creation_timestamp': datetime.utcnow(),
                'todo_id': todo_id,
                'due_date': None
            } #type: TodoLogDB
            if 'due_date' in todo_object:
                todo_log['due_date'] = todo_object['due_date']
            else:
                todo_log['due_date'] = None
            #insert into todo_logs collection
            db.execute("insert into todo_logs (todo_id, action, due_date, creation_timestamp) values (:todo_id, :action, :due_date, :creation_timestamp)", todo_log)
            conn.commit()

        conn.close()
