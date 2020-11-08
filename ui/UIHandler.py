from TodoTypes import Todo, TodoUpdatePayload, PayloadError
from TodoTypes import TodoTaskDoneOrSkipModel
from TodoTypes import TodoLog
from TodoTypes import TaskBuckets
from typing import List, Any
from flask import render_template, request, redirect
from ui import TaskUtils as task_utils
from datetime import datetime
from dbManager import DBManager
from typing import Union

#__database: DBManager
#__app: Any

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

def __filter_task():
    return render_template("filter.html")

# Validations
def __validateTimeSlot(timeSlot):
    if timeSlot and (timeSlot.isdigit()):
        timeSlot = int(timeSlot)
        if not (timeSlot >= 1 and timeSlot <= 6):
            return False
    return True

def __validateRemindBeforeDays(remind):
    if remind and (not remind.isdigit()):
        return False
    return True


def __validateDueDate(dueDate):
    try:
        if dueDate:
            task_utils.get_local_datetime_object(dueDate).timestamp()
    except ValueError:
        return False
    return True


def __validateCreateEditPayload(formData) -> Union[PayloadError, TodoUpdatePayload]:
    errors = {"globalErrors": []}  # type: PayloadError

    if(__validateTimeSlot(formData.get("slot")) is False):
        errors["globalErrors"].append("Invalid Time Slot")

    if(__validateRemindBeforeDays(formData.get('remindBeforeDays')) is False):
        errors["globalErrors"].append("Remind before days should be a number")

    if(__validateDueDate(formData.get('dueDate')) is False):
        errors["globalErrors"].append("Invalid Due Date. Format should be yyyy-MM-DD")

    if len(errors["globalErrors"]) > 0:
        return errors

    data = {"due_date": None,
            "frequency": formData.get('frequency'),
            "task": formData.get('taskTitle'),
            "timeSlot": formData.get("slot"),
            "remindBeforeDays": formData.get('remindBeforeDays'),
            "trackHabit": formData.get("trackHabit") == "on"
            }  # type: TodoUpdatePayload

    if 'dueDate' in formData and formData['dueDate'] != "":
        data['due_date'] = task_utils.get_local_datetime_object(formData["dueDate"]).timestamp()

    return data


# routes
def __edit_task(todo_id):
    formData = request.form
    data = __validateCreateEditPayload(formData)
    if "globalErrors" in data:
        return __edit_task_page(todo_id, data)
    __database.upsert_todo(todo_id, data)
    return redirect("/todos/home", 302)


def __create_task():
    formData = request.form
    data = __validateCreateEditPayload(formData)
    if "globalErrors" in data:
        return __load_create_new_page(data)
    if 'dueDate' in formData and formData['dueDate'] != "":
        data['due_date'] = task_utils.get_local_datetime_object(formData["dueDate"]).timestamp()
    __database.create_todo(data)
    return redirect("/todos/home", 302)


def __edit_task_page(todo_id, errors=None):
    todo = __database.get_todo(todo_id)
    return render_template("editCreateTask.html",
                           data={"action": "edit",
                                 "taskData": todo and task_utils.get_task_view_model(todo, {}, request.accept_languages),
                                 "errors": errors})

def __load_create_new_page(errors=None):
    return render_template("editCreateTask.html", data={"action": "create", "taskData": None, "errors": errors})

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
        bucket = task_utils.get_task_bucket(todo).name
        todos_by_type[bucket].append(task_utils.get_task_view_model(todo, todo_logs_map, request.accept_languages))

    task_utils.sort_task_by_slots(todos_by_type[TaskBuckets.TODAY.name])
    return render_template("homepage.html", todos=todos_by_type, errors=errors, filterString=filterString)


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
            if __validateDueDate(submittedData[x]['next_due']) is False:
                errors['globalErrors'].append("Invalid Due Date Detected")
            dataToProcess[x] = submittedData[x]

    if len(errors['globalErrors']) > 0:
        return __home_page(errors)

    for dataKey in dataToProcess:
        data = dataToProcess[dataKey]
        due_date = data.get("next_due") and datetime.utcfromtimestamp(task_utils.get_local_datetime_object(data['next_due']).timestamp())
        todo_data = {'due_date': due_date, 'todo_action': data['done_or_skip'], 'todo_id': dataKey}  # type: TodoTaskDoneOrSkipModel
        __database.process_todo_action(todo_data)
    return __home_page()
