import json
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.json_util import dumps
import simpleTodoDataAccess


APP = Flask(__name__)

if APP.config['ENV'] == "automatedTesting":
    APP.config['MONGO_URI'] = "mongodb://localhost:27017/automatedTesting"
else:
    APP.config['MONGO_URI'] = "mongodb://localhost:27017/simpleTodo"

MONGO = PyMongo(APP)
TODO_DATA = simpleTodoDataAccess.SimpleTodoDataAccess(MONGO);

@APP.route('/todos', methods=['GET'])
def all_todos():
    """Gets all todos from data source, sorted by due date in ascending order"""
    data = TODO_DATA.get_all_todos_by_due_date()
    return jsonify(json.loads(dumps(data)))



@APP.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a specific todo"""
    todo = TODO_DATA.get_todo(todo_id)
    data = []
    data.append(todo)
    return jsonify(json.loads(dumps(data)))


@APP.route('/todos', methods=['POST'])
def create_todos():
    data = request.get_json()
    TODO_DATA.create_todo(data)
    return jsonify(json.loads(dumps(data)))

@APP.route('/todos/<int:todo_id>', methods=['POST'])
def update_or_create_todo(todo_id): #id is not auto generated
    data = request.get_json()
    TODO_DATA.upsert_todo(todo_id, data)
    return jsonify(json.loads(dumps(data)))


@APP.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    TODO_DATA.delete_todo(todo_id)
    return jsonify({})



@APP.route('/todos/logs/stats', methods=['GET'])
def get_todo_logs_counts_by_action():
    stats = TODO_DATA.get_todo_logs_count()
    data = []
    data.append(stats)
    return jsonify(json.loads(dumps(data)))




if __name__ == "__main__":
    APP.run(debug=True, host='0.0.0.0')
