import json
from flask import Flask, jsonify, request
from bson.json_util import dumps
import dbManager
from ui import UIHandler as ui
from datetime import datetime

APP = Flask(__name__)
TODO_DATA = dbManager.getDataAccessObject(APP)

ui.init_ui(APP, TODO_DATA)

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
def update_or_create_todo(todo_id):  # id is not auto generated
    data = request.get_json()
    TODO_DATA.upsert_todo(todo_id, data)
    return jsonify(json.loads(dumps(data)))


@APP.route('/todos/action/<int:todo_id>', methods=['POST'])
def todo_action(todo_id):  # id is not auto generated
    data = request.get_json()
    data["due_date"] = datetime.utcfromtimestamp(data['due_date'])
    TODO_DATA.process_todo_action(data)
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
