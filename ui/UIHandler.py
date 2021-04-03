from TodoTypes import Todo, TodoUpdatePayload, PayloadError
from TodoTypes import TodoTaskDoneOrSkipModel, TodoCreatePayload
from TodoTypes import TodoLog
from TodoTypes import TaskBuckets
from flask import render_template, request, redirect, make_response, Flask
from ui import TaskUtils as task_utils
from datetime import datetime
from db.dbManager import DBManager
from util import commons
from runtime_type_checker import check_type
from typing import List

__database: DBManager
__app: Flask

def init_ui(app, dbConnection: DBManager):
    global __database
    __database = dbConnection
    global __app
    __app = app
    __app.add_url_rule("/todos/home", "home", __home_page, methods=["GET"])
    __app.add_url_rule("/todos/home", "submit", __process_updates, methods=["POST"])
    __app.add_url_rule("/todos/new/task", "new", __load_create_new_page, methods=["GET"])
    __app.add_url_rule("/todos/edit/<int:todo_id>", "edit", __edit_task_page, methods=["GET"])
    __app.add_url_rule("/todos/new/task", "createTask", __create_task, methods=["POST"])
    __app.add_url_rule("/todos/edit/<int:todo_id>", "editTask", __edit_task, methods=["POST"])
    __app.add_url_rule("/todos/filter", "filter", __filter_task, methods=["GET"])
    __app.add_url_rule("/todos/style", "style", __generate_style, methods=["GET"])
    __app.add_url_rule("/todos/delete/<int:todo_id>", "delete", __delete_task_page, methods=["GET"])
    __app.add_url_rule("/todos/delete/<int:todo_id>", "deleteTask", __delete_task, methods=["POST"])

def __generate_style():
    resp = make_response(render_template("style.css", commons=commons))
    resp.headers['Content-Type'] = 'text/css'
    return resp


def __filter_task():
    return render_template("filter.html", commons=commons)


# routes
def __delete_task(todo_id):
    __database.delete_todo(todo_id)
    return redirect("/todos/home", 302)

def __edit_task(todo_id):
    formData = request.form
    data = commons.validateCreateEditPayload(formData, todo_id)
    if "globalErrors" in data:
        return __edit_task_page(todo_id, data)
    check_type(data, TodoUpdatePayload)
    __database.upsert_todo(todo_id, data)
    return redirect("/todos/home", 302)


def __create_task():
    formData = request.form
    data: TodoCreatePayload = commons.validateCreateEditPayload(formData)
    if "globalErrors" in data:
        return __load_create_new_page(data)
    check_type(data, TodoCreatePayload)
    __database.create_todo(data)
    return redirect("/todos/home", 302)


def __edit_task_page(todo_id, errors=None):
    todo = __database.get_todo(todo_id)
    return render_template("editCreateTask.html",
                           data={"action": "edit",
                                 "taskData": todo and task_utils.get_task_view_model(todo, {}, request.accept_languages),
                                 "errors": errors, "commons": commons})

def __delete_task_page(todo_id, errors=None):
    todo = __database.get_todo(todo_id)
    return render_template("deleteTask.html", data={"action": "delete",
                                                    "taskData": todo and task_utils.get_task_view_model(todo, {}, request.accept_languages)})


def __load_create_new_page(errors=None):
    return render_template("editCreateTask.html", data={"action": "create", "taskData": None, "errors": errors, "commons": commons})

def __home_page(errors=None):
    filterString = ""
    if request.args.get("query"):
        filters = __database.parseFilters(request.args.get("query"))
        if filters:
            filterString = request.args.get("query")
    else:
        filters = []
    allTodos = __database.get_all_todos_by_due_date(filters)  # type: List[Todo]
    todo_logs = __database.get_todo_logs_count()  # type: TodoLog
    todo_logs_map = {}
    for log in todo_logs:
        if log["todo_id"] not in todo_logs_map:
            todo_logs_map[log["todo_id"]] = {}
        todo_logs_map[log["todo_id"]][log["action"]] = log["count"]

    todos_by_type = {
        TaskBuckets.ALERTS.name: [],
        TaskBuckets.PENDING.name: [],
        TaskBuckets.TODAY.name: [],
        TaskBuckets.UPCOMING.name: []
    }

    for todo in allTodos:
        check_type(todo, Todo)
        bucket = task_utils.get_task_bucket(todo).name
        todos_by_type[bucket].append(task_utils.get_task_view_model(todo, todo_logs_map, request.accept_languages))

    task_utils.sort_task_by_slots(todos_by_type[TaskBuckets.TODAY.name])
    return render_template("homepage.html", todos=todos_by_type, errors=errors, filterString=filterString, commons=commons)


def __process_updates():
    errors = {"globalErrors": []}  # type: PayloadError
    formData = request.form
    submittedData = {}
    for dataKey in formData:
        data = formData[dataKey]
        delimiter = dataKey.find("_")
        if delimiter == -1:
            errors["globalErrors"].append("Invalid Parameter detected")
            continue
        todo_id = dataKey[0:delimiter]
        attribute = dataKey[delimiter+1:]
        if todo_id not in submittedData:
            submittedData[todo_id] = {}
        submittedData[todo_id][attribute] = data

    if len(errors['globalErrors']) > 0:
        return __home_page(errors)

    # Start to process data with actions
    dataToProcess = {}
    for x in submittedData:
        if 'done_or_skip' in submittedData[x] and submittedData[x]['done_or_skip'] != "None":
            if commons.validateDueDate(submittedData[x]['next_due']) is False:
                errors['globalErrors'].append("Invalid Due Date Detected")
            dataToProcess[x] = submittedData[x]

    if len(errors['globalErrors']) > 0:
        return __home_page(errors)

    for dataKey in dataToProcess:
        data = dataToProcess[dataKey]
        due_date = data.get("next_due") and datetime.utcfromtimestamp(task_utils.get_local_datetime_object(data['next_due']).timestamp())
        todo_data = {'due_date': due_date, 'todo_action': data['done_or_skip'], 'todo_id': int(dataKey)}  # type: TodoTaskDoneOrSkipModel
        check_type(todo_data, TodoTaskDoneOrSkipModel)
        __database.process_todo_action(todo_data)
    return __home_page()
