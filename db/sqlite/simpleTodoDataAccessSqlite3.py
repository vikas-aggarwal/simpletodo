from datetime import datetime
import sqlite3
from TodoTypes import Todo, TodoLog, TodoCreatePayload, TodoTaskDoneOrSkipModel
from TodoTypes import TodoUpdatePayload, FilterModel, TodoLogEntry
from TodoTypes import TodoLogDB
from db.dbManager import DBManager
from typing import Dict, Any, Optional, List
from db.sqlite import upgradeSqliteDatabase


class SimpleTodoDataAccessSqlite3(DBManager):
    TODO_SELECT_COLUMN_STRING = "todo_id, due_date as 'due_date [timestamp]', frequency, remind_before_days, task_name, time_slot, todo_action, track_habit, category"
    dbMap = {"task": "task_name",
             "frequency": "frequency",
             "trackHabit": "track_habit",
             "category": "category",
             "timeSlot": "time_slot",
             "due_date": "due_date"
             }

    def __init__(self, APP):
        self.db_path = APP.config['SQLITE3_DB_PATH']
        self.detect_types = sqlite3.PARSE_COLNAMES

        # Create schema is does not exists
        conn = self._getConnection()
        upgradeSqliteDatabase.process(conn, self.getSchemaVersion())
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
                "remindBeforeDays": int(row['remind_before_days'] or "0"),
                "category": row['category']
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

    def _getTodoLogEntryFromRow(self,row) -> TodoLogEntry:
        todo_log_entry: TodoLogEntry = {
            "task": row['task_name'],
            "due_date": row['due_date'],
            "action": row['action'],
            "todo_id": row['todo_id']
        }
        return todo_log_entry
    
    def get_todo_logs(self, startTimeStamp: datetime, endTimeStamp: datetime) -> List[TodoLogEntry]:
        conn = self._getConnection()
        db = conn.cursor()
        db.execute("select t.todo_id, t.task_name, l.due_date as 'due_date [timestamp]', l.action from todos t, todo_logs l where t.todo_id = l.todo_id and datetime(l.due_date) between ? and ? order by 1,2",
                   (startTimeStamp, endTimeStamp))
        data = []
        rows = db.fetchall()
        for row in rows:
            data.append(self._getTodoLogEntryFromRow(row))
        return data

    def __generateConditionsForFilters(self, filters: FilterModel):
        condition = "1=1"
        values = []
        for filterUnit in filters:
            attribute = filterUnit["attribute"]
            operator = filterUnit["operator"]
            value = filterUnit["value"]
            # Use of coalesce needs to be re-evaluated for queries using NULL in the future.
            if operator == "IN":
                condition = condition + " AND COALESCE(" + self.dbMap[attribute] + ",'') " + operator + " ("
                for val in range(0, len(value)):
                    if val == 0:
                        condition = condition + " ? "
                    else:
                        condition = condition + ", ? "
                    if "trackHabit" == attribute:
                        values.append("True" == value[val])
                    elif "timeSlot" == attribute:
                        values.append(int(value[val]))
                    else:
                        values.append(value[val])
                condition = condition + ") "

            else:
                condition = condition + " AND COALESCE(" + self.dbMap[attribute] + ",'') " + operator + " ? "
                if operator == "LIKE":
                    value = "%"+value+"%"
                if "trackHabit" == attribute:
                    values.append("True" == value)
                elif "timeSlot" == attribute:
                    values.append(int(value))
                else:
                    values.append(value)
        return [condition, tuple(values)]

    def get_all_todos_before_date(self, filters: Optional[FilterModel], sort_criteria, current_date):
        conn = self._getConnection()
        db = conn.cursor()
        condition = "1=1"
        values = ()
        if filters:
            conditionAndValues = self.__generateConditionsForFilters(filters)
            condition = conditionAndValues[0]
            values = conditionAndValues[1]
        condition = condition + " AND (datetime(due_date) <= ? or due_date is null)"  # Hack: Always list null
        values_list = list(values)
        values_list.append(current_date)
        values = tuple(values_list)
        final_query = "select " + self.TODO_SELECT_COLUMN_STRING + " from todos where "+condition
        if sort_criteria:
            final_query = final_query + " order by "
            for index in range(0, len(sort_criteria)):
                if index == 0:
                    final_query = final_query + " " + self.dbMap[sort_criteria[index]]
                else:
                    final_query = final_query + ", " + self.dbMap[sort_criteria[index]]
        db.execute(final_query, values)
        data = []
        rows = db.fetchall()
        for row in rows:
            todo = self._getTodoObjectFromRow(row)  # type: Todo
            data.append(todo)
        return data

    def get_all_todos_by_due_date(self, filters: Optional[FilterModel]):
        conn = self._getConnection()
        db = conn.cursor()
        condition = "1=1"
        values = ()
        if filters:
            conditionAndValues = self.__generateConditionsForFilters(filters)
            condition = conditionAndValues[0]
            values = conditionAndValues[1]

        db.execute("select " + self.TODO_SELECT_COLUMN_STRING + " from todos where "+condition+" order by datetime(due_date), time_slot", values)
        data = []
        rows = db.fetchall()
        for row in rows:
            todo = self._getTodoObjectFromRow(row)  # type: Todo
            data.append(todo)
        return data

    def get_todo(self, todo_id: int):
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
            dbObject['due_date'] = data['due_date']
        else:
            dbObject['due_date'] = None

        dbObject['remindBeforeDays'] = data.get('remindBeforeDays')
        dbObject['timeSlot'] = data.get('timeSlot')
        dbObject['trackHabit'] = data.get('trackHabit')
        dbObject['frequency'] = data.get('frequency')
        dbObject['task'] = data.get('task')
        dbObject['category'] = data.get('category')

        if todo_id is None:
            db.execute("insert into todos (todo_id, due_date, frequency, remind_before_days, task_name, time_slot, todo_action, track_habit, category) values ((select coalesce(max(todo_id),count(*))+1 from todos), :due_date, :frequency, :remindBeforeDays, :task, :timeSlot, NULL, :trackHabit, :category )", dbObject)
            last_row_id = db.lastrowid
            db.execute("select todo_id from todos where rowid = ?", (last_row_id,))
            row = db.fetchone()
            data["todo_id"] = row["todo_id"]
        else:
            data["todo_id"] = todo_id
            db.execute("insert into todos (todo_id, due_date, frequency, remind_before_days, task_name, time_slot, todo_action, track_habit, category) values (:todo_id, :due_date, :frequency, :remindBeforeDays, :task, :timeSlot, NULL, :trackHabit, :category)", dbObject)
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

        if "trackHabit" not in data:
            data['trackHabit'] = todo_object['trackHabit']

        data['todo_id'] = todo_id

        # get remaining data from payload or existing object
        data['frequency'] = data.get('frequency') if "frequency" in data else todo_object['frequency']
        data['task'] = data.get('task') if "task" in data else todo_object['task']
        data['timeSlot'] = data.get('timeSlot') if "timeSlot" in data else todo_object['timeSlot']
        data['remindBeforeDays'] = data.get('remindBeforeDays') if "remindBeforeDays" in data else todo_object['remindBeforeDays']
        data['category'] = data.get('category') if "category" in data else todo_object['category']
        db.execute("update todos set due_date=:due_date," \
                   "frequency=:frequency, remind_before_days=:remindBeforeDays," \
                   "task_name=:task, time_slot=:timeSlot, track_habit=:trackHabit," \
                   "category=:category where todo_id = :todo_id", data)
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
