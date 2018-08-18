from flask import Flask,jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import dumps
import json
import pymongo
import os

from datetime import datetime

app=Flask(__name__)

if "OPENSHIFT_MONGODB_DB_HOST" in os.environ :
    app.config['MONGO_HOST']=os.environ.get("OPENSHIFT_MONGODB_DB_HOST")
    app.config['MONGO_DBNAME']="simpletodo"

if "OPENSHIFT_MONGODB_DB_PORT" in os.environ :
    app.config['MONGO_PORT']=os.environ.get("OPENSHIFT_MONGODB_DB_PORT")

if "OPENSHIFT_MONGODB_DB_USERNAME" in os.environ :
    app.config['MONGO_USERNAME']=os.environ.get("OPENSHIFT_MONGODB_DB_USERNAME")

if "OPENSHIFT_MONGODB_DB_PASSWORD" in os.environ :
    app.config['MONGO_PASSWORD']=os.environ.get("OPENSHIFT_MONGODB_DB_PASSWORD")



mongo=PyMongo(app)


@app.route('/todos', methods=['GET'])
def all_todos():
    all_todos = mongo.db.todos.find({}).sort('due_date',pymongo.ASCENDING)
    data = [];
    for todo in all_todos:
        data.append(todo);
    return jsonify(json.loads(dumps(data)));


def get_todo_object(todo_id):
    return mongo.db.todos.find_one({'todo_id':todo_id})
    

@app.route('/todos/<int:todo_id>' , methods=['GET'])
def get_todo(todo_id):
    todo=get_todo_object(todo_id);
    data=[];
    data.append(todo);
    return jsonify(json.loads(dumps(data)))


@app.route('/todos', methods=['POST'])
def create_todos():
    data=request.get_json();
    if 'due_date' in data:
        data['due_date']=datetime.utcfromtimestamp(data['due_date'])
    max_data = list(mongo.db.todos.aggregate([{"$group":{"_id": "","max_id": { "$max": "$todo_id" }}}]));
    max_todo_id=1
    for item in list(max_data):
        print(item)
        if (item['max_id'] is None):
            max_todo_id=1
        else:
            print(item['max_id'])
            print(type(item['max_id']))
            max_todo_id=item['max_id']+1
            
    data['todo_id']=max_todo_id
    mongo.db.todos.insert_one(data);
    return jsonify(json.loads(dumps(data)));

@app.route('/todos/<int:todo_id>' , methods=['POST'])
def update_or_create_todo(todo_id): #id is not auto generated

    #Getting current state
    todo_object = get_todo_object(todo_id);
    data=request.get_json();
    if 'due_date' in data:
        data['due_date']=datetime.utcfromtimestamp(data['due_date'])

    data['todo_id']=todo_id
    mongo.db.todos.update_one({'todo_id':todo_id},{'$set': data},upsert=True);

    #if obtained via an action log it
    if ('trackHabit' in todo_object) and todo_object['trackHabit']==True :
        todo_log={};
        todo_log['action']=data['todo_action'];
        todo_log['creation_timestamp']=datetime.utcnow();
        todo_log['todo_id']=todo_id;

        if 'due_date' in todo_object:
            todo_log['due_date']=todo_object['due_date'];
            #insert into todo_logs collection
            mongo.db.todo_logs.insert(todo_log);
    
    return jsonify(json.loads(dumps(data)))


@app.route('/todos/<int:todo_id>' , methods=['DELETE'])
def delete_todo(todo_id):
    mongo.db.todos.find_one_and_delete({'todo_id':todo_id})
    mongo.db.todo_logs.delete_many({'todo_id':todo_id});
    return jsonify({})

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
