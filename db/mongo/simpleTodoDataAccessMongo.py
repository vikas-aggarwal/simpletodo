from datetime import datetime
import pymongo
from pymongo import MongoClient
from db.dbManager import DBManager
from TodoTypes import FilterModel, Todo, TodoLog, TodoLogEntry
from typing import Optional, List

class SimpleTodoDataAccessMongo(DBManager):
    def __init__(self, APP):
        mongo = MongoClient(APP.config['MONGO_HOST'], APP.config['MONGO_PORT'])
        self.db = mongo[APP.config['MONGO_DB']]

    def get_todo_logs_count(self):
        todo_count = self.db.todo_logs.aggregate([
            {"$group":{"_id":{"action":"$action", "todo_id":"$todo_id"}, "count":{"$sum": 1}}}])
        data=[]
        for row in todo_count:
            data.append(self._getTodoLogObjectFromRow(row))
        return data

    def _getTodoLogEntryFromRow(self, row, todo_id_map) -> TodoLogEntry:
        todo_log_entry: TodoLogEntry = {
            "task": todo_id_map[row['todo_id']],
            "due_date": row['due_date'],
            "action": row['action'],
            "todo_id": row['todo_id']
        }
        return todo_log_entry

    def get_todo_logs(self, startTimeStamp: datetime, endTimeStamp: datetime) -> List[TodoLogEntry]:
        todo_logs = self.db.todo_logs.find({"due_date": {"$lte": endTimeStamp, "$gte": startTimeStamp}})
        todo_id_map = {}
        todos = self.db.todos.find(projection=["task","todo_id"])

        for todo in todos:
            todo_id_map[todo['todo_id']] = todo['task']
            
        data = []
        for todo_log in todo_logs:
            data.append(self._getTodoLogEntryFromRow(todo_log, todo_id_map))
        return data
    
    def _getTodoLogObjectFromRow(self, row):
        todo_log = {"todo_id": row['_id']['todo_id'], "action":row['_id']['action'], "count" : row['count']} #type: TodoLog
        return todo_log

    def _getTodoObjectFromRow(self, row):

        if row is None:
            return None

        todo = {"todo_id": row['todo_id'],
                "due_date": row.get('due_date'),
                "frequency": row.get('frequency'),
                "task": row['task'],
                "timeSlot": None,
                "trackHabit": (row.get('trackHabit') == 1),
                "remindBeforeDays": int(row.get('remindBeforeDays') or "0"),
                "category": row.get('category'),
                "duration": row.get('duration'),
                "description": row.get('description')
                }  # type: Todo
        if row.get('timeSlot') and row.get('timeSlot') == "None":
            todo['timeSlot'] = None
        elif row.get('timeSlot'):
            todo['timeSlot'] = int(row.get('timeSlot'))
        return todo

    def _get_filter_object(self, filters: Optional[FilterModel]):
        operator_map = {
            "=": "$eq",
            "!=": "$ne",
            "IN": "$in"
        }
        final_filter = {}
        if filters:
            final_filter = {"$and": []}
            for filterUnit in filters:
                attribute = filterUnit["attribute"]
                operator = filterUnit["operator"]
                value = filterUnit["value"]
                if attribute == "timeSlot":
                    if operator == "IN":
                        value = [int(x) for x in value]
                    else:
                        value = int(value)
                if operator == "LIKE":
                    final_filter["$and"].append({attribute: {"$regex": value}})
                else:
                    final_filter["$and"].append({attribute: {operator_map[operator]: value}})
        return final_filter

    def get_all_todos_before_date(self, filters: Optional[FilterModel], sort_criteria, current_date):
        filter_object = self._get_filter_object(filters)
        if filter_object:
            filter_object["$and"].append({"due_date": {"$lte": current_date}})
        else:
            filter_object = {"due_date": {"$lte": current_date}}
        if sort_criteria:
            sort_array = []
            for index in range(0, len(sort_criteria)):
                sort_array.append((sort_criteria[index], pymongo.ASCENDING))
            all_todos = self.db.todos.find(self._get_filter_object(filters)).sort(sort_array)
        else:
            all_todos = self.db.todos.find(self._get_filter_object(filters))
        data = []
        for todo in all_todos:
            data.append(self._getTodoObjectFromRow(todo))
        return data

    def get_all_todos_by_due_date(self, filters: Optional[FilterModel]):
        all_todos = self.db.todos.find(self._get_filter_object(filters)).sort('due_date', pymongo.ASCENDING)
        data = []
        for todo in all_todos:
            data.append(self._getTodoObjectFromRow(todo))
        return data

    def get_todo(self, todo_id: int):
        todo = self.db.todos.find_one({'todo_id':todo_id})
        return todo and self._getTodoObjectFromRow(todo)

    def create_todo(self, data):
        max_data = list(self.db.todos.aggregate([
            {"$group":{"_id": "", "max_id":{"$max": "$todo_id"}}}]))
        max_todo_id = 1
        for item in list(max_data):
            if item['max_id'] is None:
                max_todo_id = 1
            else:
                max_todo_id = item['max_id']+1

        data['todo_id'] = max_todo_id
        self.db.todos.insert_one(data)

    def delete_todo(self, todo_id):
        self.db.todos.find_one_and_delete({'todo_id':todo_id})
        self.db.todo_logs.delete_many({'todo_id':todo_id})

    def upsert_todo(self, todo_id, data):
        #Getting current state
        todo_object = self.get_todo(todo_id)

        data['todo_id'] = todo_id
        self.db.todos.update_one({'todo_id':todo_id}, {'$set': data}, upsert=True)

        #Delete todo logs if no longer tracked as Habit
        if (('trackHabit' in todo_object) and
                todo_object['trackHabit'] and
                ('trackHabit' in data) and (not data['trackHabit'])):
            self.db.todo_logs.delete_many({'todo_id':todo_id})
            return

        #if obtained via an action log it
        if ('trackHabit' in todo_object) and todo_object['trackHabit'] and ('todo_action' in data):
            todo_log = {}
            todo_log['action'] = data['todo_action']
            todo_log['creation_timestamp'] = datetime.utcnow()
            todo_log['todo_id'] = todo_id

            if 'due_date' in todo_object:
                todo_log['due_date'] = todo_object['due_date']
                #insert into todo_logs collection
                self.db.todo_logs.insert_one(todo_log)

    def process_todo_action(self, data):

        data['todo_id'] = int(data['todo_id'])
        #Getting current state
        todo_object = self.get_todo(data['todo_id'])
        self.db.todos.update_one({'todo_id':data['todo_id']}, {'$set': data})
        
        if ('trackHabit' in todo_object) and todo_object['trackHabit']:
            todo_log = {}
            todo_log['action'] = data['todo_action']
            todo_log['creation_timestamp'] = datetime.utcnow()
            todo_log['todo_id'] = data['todo_id']

            if 'due_date' in todo_object:
                todo_log['due_date'] = todo_object['due_date']
                #insert into todo_logs collection
                self.db.todo_logs.insert_one(todo_log)

    def get_categories(self):
        categories = {}
        categoryDocuments = self.db.categories.find()
        category_found = False
        for category in categoryDocuments:
            category_found = True
            categories[category["internal_name"]] = {"internal_name": category["internal_name"],
                               "display_name": category["display_name"],
                               "background_color": category["background_color"]}
        if category_found != True:
            seed_categories = [{"internal_name":"uncategorized","display_name":"Uncategorized","background_color":"#ceecce"},
                               {"internal_name":"health","display_name":"Health","background_color":"#9eb0e3"},
                               {"internal_name":"finance","display_name":"Finance","background_color":"#eae485"},
                               {"internal_name":"maintenance","display_name":"Maintenance","background_color":"#e8bdbd"},
                               {"internal_name":"bills","display_name":"Bills","background_color":"#A0CCDB"},
                               {"internal_name":"learning","display_name":"Learning","background_color":"#d5af56"}]

            self.db.categories.insert_many(seed_categories)
            categoryDocuments = self.db.categories.find()
            category_found = False
            for category in categoryDocuments:
                category_found = True
                categories[category["internal_name"]] = {"internal_name": category["internal_name"],
                                                         "display_name": category["display_name"],
                                                         "background_color": category["background_color"]}
        return categories

    def create_category(self, data):
        existing_category = self.db.categories.find_one({"internal_name": {"$eq": data["internal_name"]}})
        if existing_category is None:
            self.db.categories.insert_one(data)
        else:
            raise Exception("Category already present")
