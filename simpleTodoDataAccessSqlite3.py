from datetime import datetime
import sqlite3
from TodoTypes import Todo, TodoLog, TodoCreatePayload, TodoTaskDoneOrSkipModel
from TodoTypes import TodoUpdatePayload, FilterModel
from TodoTypes import TodoLogDB
from dbManager import DBManager
from typing import Dict, Any

class SimpleTodoDataAccessSqlite3(DBManager):
    TODO_SELECT_COLUMN_STRING = "todo_id, due_date as 'due_date [timestamp]', frequency, remind_before_days, task_name, time_slot, todo_action, track_habit"

    def __init__(self, APP):
        self.db_path = APP.config['SQLITE3_DB_PATH']
        self.detect_types = sqlite3.PARSE_COLNAMES

        # Create schema is does not exists
        conn = self._getConnection()
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
        conn = sqlite3.connect(self.db_path, detect_types=self.detect_types)
        conn.row_factory = sqlite3.Row
        return conn

    def _getTodoObjectFromRow(self, row):

        if row is None:
            return None

        todo = {"todo_id": row['todo_id'],
                "due_date": row['due_date'],
                "frequency": row['frequency'],
                "task": row['task_name'],
                "timeSlot": row['time_slot'],
                "trackHabit": (row['track_habit'] == 1),
                "remindBeforeDays": int(row['remind_before_days'] or "0")
                }  # type: Todo
        return todo

    def _getTodoLogObjectFromRow(self, row):
        todo_log = {"todo_id": row['todo_id'], "action": row['action'], "count": row['count']}  # type: TodoLog
        return todo_log

    def get_todo_logs_count(self):
        conn = self._getConnection()
        db = conn.cursor()
        db.execute("select count(*) as count,todo_id,action from todo_logs group by todo_id,action")
        data = []
        rows = db.fetchall()
        for row in rows:
            data.append(self._getTodoLogObjectFromRow(row))
        return data

    def __generateConditionsForFilters(self, filters: FilterModel):
        condition = "1=1"
        dbMap = {"task": "task_name",
                 "frequency": "frequency",
                 "trackHabit": "track_habit"
                 }
        values = []
        for filterUnit in filters:
            attribute = filterUnit["attribute"]
            operator = filterUnit["operator"]
            value = filterUnit["value"]

            condition = condition + " AND " + dbMap[attribute] + " " + operator + " ? "
            if "trackHabit" == attribute:
                values.append("True" == value)
            else:
                values.append(value)
        return [condition, tuple(values)]

    def get_all_todos_by_due_date(self, filters: FilterModel):
        conn = self._getConnection()
        db = conn.cursor()
        condition = "1=1"
        values = ()
        if filters:
            conditionAndValues = self.__generateConditionsForFilters(filters)
            condition = conditionAndValues[0]
            values = conditionAndValues[1]

        db.execute("select " + self.TODO_SELECT_COLUMN_STRING + " from todos where "+condition+" order by datetime(due_date)", values)
        data = []
        rows = db.fetchall()
        for row in rows:
            todo = self._getTodoObjectFromRow(row)  # type: Todo
            data.append(todo)
        return data

    def get_todo(self, todo_id):
        conn = self._getConnection()
        db = conn.cursor()
        db.execute("select "+self.TODO_SELECT_COLUMN_STRING+" from todos where todo_id = ?", (todo_id,))
        row = db.fetchone()
        return self._getTodoObjectFromRow(row)

    def create_todo(self, data: TodoCreatePayload, todo_id=None):
        dbObject = {}  # type: Dict[str, Any]
        conn = self._getConnection()
        db = conn.cursor()
        if data.get('due_date') is not None:
            due_date_from_payload: int = data['due_date'] or 0
            dbObject['due_date'] = datetime.utcfromtimestamp(due_date_from_payload)
        else:
            dbObject['due_date'] = None

        dbObject['remindBeforeDays'] = data.get('remindBeforeDays')
        dbObject['timeSlot'] = data.get('timeSlot')
        dbObject['trackHabit'] = data.get('trackHabit')
        dbObject['frequency'] = data.get('frequency')
        dbObject['task'] = data.get('task')

        if todo_id is None:
            db.execute("insert into todos (todo_id, due_date, frequency, remind_before_days, task_name, time_slot, todo_action, track_habit) values ((select coalesce(max(todo_id),count(*))+1 from todos), :due_date, :frequency, :remindBeforeDays, :task, :timeSlot, NULL, :trackHabit )", dbObject)
            last_row_id = db.lastrowid
            db.execute("select todo_id from todos where rowid = ?", (last_row_id,))
            row = db.fetchone()
            data["todo_id"] = row["todo_id"]
        else:
            data["todo_id"] = todo_id
            db.execute("insert into todos (todo_id, due_date, frequency, remind_before_days, task_name, time_slot, todo_action, track_habit) values (:todo_id, :due_date, :frequency, :remindBeforeDays, :task, :timeSlot, NULL, :trackHabit )", dbObject)
        conn.commit()
        conn.close()

    def delete_todo(self, todo_id):
        conn = self._getConnection()
        db = conn.cursor()
        db.execute("delete from todos where todo_id = ?", (todo_id,))
        db.execute("delete from todo_logs where todo_id = ?", (todo_id,))
        conn.commit()
        conn.close()

    def upsert_todo(self, todo_id, data  # type: TodoUpdatePayload
                    ):
        # Getting current state
        todo_object = self.get_todo(todo_id)  # type: Todo

        if todo_object is None:  # insert
            self.create_todo(data, todo_id)
            return

        conn = self._getConnection()
        db = conn.cursor()

        if data.get('due_date') is None:
            data['due_date_utc'] = todo_object['due_date']
        else:
            data['due_date_utc'] = datetime.utcfromtimestamp(float(data['due_date'] or 0)) or datetime.now()

        if "trackHabit" not in data:
            data['trackHabit'] = todo_object['trackHabit']

        data['todo_id'] = todo_id

        # get remaining data from payload or existing object
        data['frequency'] = data.get('frequency') if "frequency" in data else todo_object['frequency']
        data['task'] = data.get('task') if "task" in data else todo_object['task']
        data['timeSlot'] = data.get('timeSlot') if "timeSlot" in data else todo_object['timeSlot']
        data['remindBeforeDays'] = data.get('remindBeforeDays') if "remindBeforeDays" in data else todo_object['remindBeforeDays']
        db.execute("update todos set due_date=:due_date_utc," \
                   "frequency=:frequency, remind_before_days=:remindBeforeDays," \
                   "task_name=:task, time_slot=:timeSlot, track_habit=:trackHabit" \
                   " where todo_id = :todo_id", data)
        conn.commit()

        # Delete todo logs if no longer tracked as Habit
        if (('trackHabit' in todo_object) and
                todo_object['trackHabit'] and
                ('trackHabit' in data) and (not data['trackHabit'])):
            db.execute("delete from todo_logs where todo_id = ?", (todo_id,))
            conn.commit()
            conn.close()
            return

        conn.close()

    def process_todo_action(self, data  # type: TodoTaskDoneOrSkipModel
                            ):

        todo_object = self.get_todo(data['todo_id'])  # type: Todo
        conn = self._getConnection()
        db = conn.cursor()
        
        db.execute("update todos set due_date=:due_date," \
                   "todo_action=:todo_action where todo_id = :todo_id", data)
        conn.commit()

        if ('trackHabit' in todo_object) and todo_object['trackHabit']:
            todo_log = {
                'action': data['todo_action'],
                'creation_timestamp': datetime.utcnow(),
                'todo_id': data['todo_id'],
                'due_date': todo_object['due_date'],
            }  # type: TodoLogDB

            # insert into todo_logs collection
            db.execute("insert into todo_logs (todo_id, action, due_date, creation_timestamp) values (:todo_id, :action, :due_date, :creation_timestamp)", todo_log)
            conn.commit()

        conn.close()
