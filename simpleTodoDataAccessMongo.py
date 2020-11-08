import sys
from datetime import datetime
import pymongo
from pymongo import MongoClient
from dbManager import DBManager

class SimpleTodoDataAccessMongo(DBManager):
    def __init__(self, APP):
        mongo   = MongoClient(APP.config['MONGO_HOST'], APP.config['MONGO_PORT'])
        self.db = mongo[APP.config['MONGO_DB']]

        
    def get_todo_logs_count(self):
        todo_count = self.db.todo_logs.aggregate([
            {"$group":{"_id":{"action":"$action", "todo_id":"$todo_id"}, "count":{"$sum": 1}}}])
        data=[]
        for row in todo_count:
            data.append(self._getTodoLogObjectFromRow(row))
        return data

    def _getTodoLogObjectFromRow(self, row):
        print(row)
        todo_log = {"todo_id": row['_id']['todo_id'], "action":row['_id']['action'], "count" : row['count']} #type: TodoLog
        return todo_log

    def _getTodoObjectFromRow(self, row):

        if row is None:
            return None

        todo = {"todo_id": row['todo_id'],
                "due_date": row['due_date'],
                "frequency": row['frequency'],
                "task": row['task'],
                "timeSlot": row.get('timeSlot'),
                "trackHabit": (row.get('trackHabit') == 1),
                "remindBeforeDays": int(row.get('remindBeforeDays') or "0")
                }  # type: Todo
        return todo

    def get_all_todos_by_due_date(self):
        all_todos = self.db.todos.find({}).sort('due_date', pymongo.ASCENDING)
        data = []
        for todo in all_todos:
            data.append(self._getTodoObjectFromRow(todo))
        return data


    def get_todo(self, todo_id):
        todo = self.db.todos.find_one({'todo_id':todo_id})
        return todo and self._getTodoObjectFromRow(todo)

    def create_todo(self, data):
        if 'due_date' in data and data['due_date']:
            data['due_date'] = datetime.utcfromtimestamp(data['due_date'])

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

        if 'due_date' in data:
            data['due_date'] = datetime.utcfromtimestamp(data['due_date'])

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
                self.db.todo_logs.insert(todo_log)

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
                self.db.todo_logs.insert(todo_log)

