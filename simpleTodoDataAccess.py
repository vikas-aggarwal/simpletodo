import pymongo
from datetime import datetime
import sys;

class SimpleTodoDataAccess:
    def __init__(self,mongo,wipeDatabase,environmentMode):
        self.mongo = mongo;
        if wipeDatabase and not environmentMode == "production":
            print("WIPING DATABASE",file=sys.stderr); 
            self.mongo.db.todo_logs.drop();
            self.mongo.db.todos.drop();


    def get_todo_logs_count(self):
        todo_count = self.mongo.db.todo_logs.aggregate([
            {"$group":{"_id": {"action":"$action","todo_id":"$todo_id"},"count": { "$sum": 1 }}}])
        return todo_count;

        
    def get_all_todos_by_due_date(self):
        all_todos = self.mongo.db.todos.find({}).sort('due_date',pymongo.ASCENDING)
        data = [];
        for todo in all_todos:
            data.append(todo);
        return data;
        
        
    def get_todo(self,todo_id):
        return self.mongo.db.todos.find_one({'todo_id':todo_id})

    def create_todo(self,data):
        if 'due_date' in data:
            data['due_date']=datetime.utcfromtimestamp(data['due_date'])
            
        max_data = list(self.mongo.db.todos.aggregate([{"$group":{"_id": "","max_id": { "$max": "$todo_id" }}}]));
        max_todo_id=1
        for item in list(max_data):
            if (item['max_id'] is None):
                max_todo_id=1
            else:
                max_todo_id=item['max_id']+1
                
        data['todo_id']=max_todo_id
        self.mongo.db.todos.insert_one(data);

    def delete_todo(self,todo_id):
        self.mongo.db.todos.find_one_and_delete({'todo_id':todo_id})
        self.mongo.db.todo_logs.delete_many({'todo_id':todo_id});

    def upsert_todo(self,todo_id,data):
        #Getting current state
        todo_object = self.get_todo(todo_id);
    
        if 'due_date' in data:
            data['due_date']=datetime.utcfromtimestamp(data['due_date'])

        data['todo_id']=todo_id
        self.mongo.db.todos.update_one({'todo_id':todo_id},{'$set': data},upsert=True);

        #Delete todo logs if no longer tracked as Habit
        if ('trackHabit' in todo_object) and todo_object['trackHabit']==True and ('trackHabit' in data) and data['trackHabit'] == False:
            self.mongo.db.todo_logs.delete_many({'todo_id':todo_id});
            return;
        
        #if obtained via an action log it
        if ('trackHabit' in todo_object) and todo_object['trackHabit']==True and ('todo_action' in data) :
            todo_log={};
            todo_log['action']=data['todo_action'];
            todo_log['creation_timestamp']=datetime.utcnow();
            todo_log['todo_id']=todo_id;

            if 'due_date' in todo_object:
                todo_log['due_date']=todo_object['due_date'];
                #insert into todo_logs collection
                self.mongo.db.todo_logs.insert(todo_log);
    
