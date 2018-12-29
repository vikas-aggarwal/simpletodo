from flask import Flask,jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import dumps
import json
import pymongo
import os
import simpleTodoDataAccess

from datetime import datetime

app=Flask(__name__)
app.config['MONGO_URI']="mongodb://localhost:27017/simpleTodo";

mongo=PyMongo(app)
todoData = simpleTodoDataAccess.SimpleTodoDataAccess(mongo);

@app.route('/todos', methods=['GET'])
def all_todos():
    data = todoData.get_all_todos_by_due_date();
    return jsonify(json.loads(dumps(data)));



@app.route('/todos/<int:todo_id>' , methods=['GET'])
def get_todo(todo_id):
    todo=todoData.get_todo(todo_id);
    data=[];
    data.append(todo);
    return jsonify(json.loads(dumps(data)))


@app.route('/todos', methods=['POST'])
def create_todos():
    data=request.get_json();
    todoData.create_todo(data);
    return jsonify(json.loads(dumps(data)));

@app.route('/todos/<int:todo_id>' , methods=['POST'])
def update_or_create_todo(todo_id): #id is not auto generated
    data=request.get_json();
    todoData.upsert_todo(todo_id,data);
    return jsonify(json.loads(dumps(data)))


@app.route('/todos/<int:todo_id>' , methods=['DELETE'])
def delete_todo(todo_id):
    todoData.delete_todo(todo_id);
    return jsonify({})

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
