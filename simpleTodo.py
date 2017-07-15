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

if "OPENSHIFT_MONGODB_DB_PORT" in os.environ :
    app.config['MONGO_PORT']=os.environ.get("OPENSHIFT_MONGODB_DB_PORT")
    
mongo=PyMongo(app)


@app.route('/todos', methods=['GET'])
def all_todos():
    all_todos = mongo.db.todos.find({}).sort('due_date',pymongo.ASCENDING)
    data = [];
    for todo in all_todos:
        data.append(todo);
    return jsonify(json.loads(dumps(data)));

@app.route('/todos/<int:todo_id>' , methods=['GET'])
def get_todo(todo_id):
    todo=mongo.db.todos.find({'todo_id':todo_id})
    data=[];
    for t in todo:
        data.append(t)
    return jsonify(json.loads(dumps(data)))


@app.route('/todos', methods=['POST'])
def create_todos():
    data=request.get_json();
    if 'due_date' in data:
        data['due_date']=datetime.fromtimestamp(data['due_date'])
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
    data=request.get_json();
    if 'due_date' in data:
        data['due_date']=datetime.fromtimestamp(data['due_date'])
    data['todo_id']=todo_id
    mongo.db.todos.update_one({'todo_id':todo_id},{'$set': data});
    return jsonify(json.loads(dumps(data)))


@app.route('/todos/<int:todo_id>' , methods=['DELETE'])
def delete_todo(todo_id):
    data=mongo.db.todos.find_one_and_delete({'todo_id':todo_id})
    return jsonify({})

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
