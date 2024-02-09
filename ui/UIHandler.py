from TodoTypes import Todo, TodoUpdatePayload, PayloadError
from TodoTypes import TodoTaskDoneOrSkipModel, TodoCreatePayload
from TodoTypes import TodoLog
from TodoTypes import TaskBuckets
from flask import render_template, request, redirect, make_response, Flask
from ui import TaskUtils as task_utils
from datetime import datetime, timedelta
from db.dbManager import DBManager
from util import commons
from runtime_type_checker import check_type
from typing import List
import pytz
import calendar

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
    __app.add_url_rule("/todos/habitReport", "habitReport", __habit_report, methods=["GET"])
    
def __generate_style():
    resp = make_response(render_template("style.css", commons=commons))
    resp.headers['Content-Type'] = 'text/css'
    return resp


def __filter_task():
    return render_template("filter.html", commons=commons)


# routes
def __habit_report():
    month = request.args.get("month")
    year = request.args.get("year")
    start_date = datetime(int(year), int(month), 1,0,0,0,0, tzinfo=task_utils.__get_ui_time_zone()).astimezone(pytz.UTC).replace(tzinfo=None)
    if int(month) != 12:
        end_date = (datetime(int(year), int(month)+1, 1, tzinfo=task_utils.__get_ui_time_zone()) + timedelta(days=-1))
    else:
        end_date = (datetime(int(year)+1, 1, 1, tzinfo=task_utils.__get_ui_time_zone()) + timedelta(days=-1))

    end_day = end_date.day
    end_date = end_date.astimezone(pytz.UTC).replace(tzinfo=None)
    todo_logs_entry = __database.get_todo_logs(start_date, end_date)
    todo_logs_entry_by_id = task_utils.get_task_logs_entry_by_id(todo_logs_entry)
    return render_template("habitReport.html", entries=todo_logs_entry_by_id, month=month, year=year, start_day=1, end_day=end_day)

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

def __group_by_status(allTodos, todo_logs_map, errors, filterString, till, groupBy):
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
    return render_template("homepage.html", todos=todos_by_type, errors=errors, filterString=filterString, commons=commons, partitions=["ALERTS", "PENDING", "TODAY", "UPCOMING"], till=till, groupBy=groupBy, currentMonthYear=task_utils.get_current_month_year())

def __group_by_slots(allTodos, todo_logs_map, errors, filterString, till, groupBy):
    todos_by_slot = {};
    
    for slot in commons.slots:
        todos_by_slot[commons.slots[slot]] = []
    
    for todo in allTodos:
        check_type(todo, Todo)
        if "timeSlot" not in todo or todo["timeSlot"] is None:
            todos_by_slot[commons.slots["None"]].append(task_utils.get_task_view_model(todo, todo_logs_map, request.accept_languages))
        else:
            todos_by_slot[commons.slots[str(todo["timeSlot"])]].append(task_utils.get_task_view_model(todo, todo_logs_map, request.accept_languages))

    return render_template("homepage.html", todos=todos_by_slot, errors=errors, filterString=filterString, commons=commons, partitions=commons.slots.values(), till=till, groupBy=groupBy, currentMonthYear=task_utils.get_current_month_year())

def __home_page(errors=None):
    filterString = ""
    if request.args.get("query"):
        filters = __database.parseFilters(request.args.get("query"))
        if filters:
            filterString = request.args.get("query")
    else:
        filters = []

    if request.args.get("till") and request.args.get("till") == "today":
        current_date = pytz.utc.localize(datetime.utcnow()).astimezone(task_utils.__get_ui_time_zone()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(pytz.UTC).replace(tzinfo=None)
        allTodos = __database.get_all_todos_before_date(filters, ["due_date"], current_date)  # type: List[Todo]
    elif request.args.get("till") and request.args.get("till") == "this_month":
        current_date = pytz.utc.localize(datetime.utcnow()).astimezone(task_utils.__get_ui_time_zone()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(pytz.UTC).replace(tzinfo=None)
        current_date = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])
        allTodos = __database.get_all_todos_before_date(filters, ["due_date"], current_date)  # type: List[Todo]
    else:    
        allTodos = __database.get_all_todos_by_due_date(filters)  # type: List[Todo]
    todo_logs = __database.get_todo_logs_count()  # type: TodoLog
    todo_logs_map = {}
    for log in todo_logs:
        if log["todo_id"] not in todo_logs_map:
            todo_logs_map[log["todo_id"]] = {}
        todo_logs_map[log["todo_id"]][log["action"]] = log["count"]
        
    if request.args.get("groupBy"):
        if request.args.get("groupBy") == "slots":
            return __group_by_slots(allTodos, todo_logs_map, errors, filterString, request.args.get("till"), request.args.get("groupBy"))
       
    return __group_by_status(allTodos, todo_logs_map, errors, filterString, request.args.get("till"), request.args.get("groupBy"))


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
