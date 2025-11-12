from TodoTypes import Todo, TodoUpdatePayload
from TodoTypes import TodoTaskDoneOrSkipModel, TodoCreatePayload, CategoryCreateEditPayload
from TodoTypes import TaskBuckets, TodoLog, PayloadError
from flask import render_template, request, redirect, make_response, Flask, url_for, send_file
from ui import TaskUtils as task_utils
from datetime import datetime, timedelta, date
from db.dbManager import DBManager
from util import commons, recur, thermalPrintImageGenerator
from runtime_type_checker import check_type
from zoneinfo import ZoneInfo
import calendar
from typing import List


__database: DBManager
__app: Flask

def init_ui(app, dbConnection: DBManager):
    global __database
    __database = dbConnection
    global __app
    __app = app
    __app.add_url_rule("/todos/home", "home", __home_page, methods=["GET"])
    __app.add_url_rule("/todos/home", "processUpdates", __process_updates, methods=["POST"])
    __app.add_url_rule("/todos/new/task", "newPage", __load_create_new_page, methods=["GET"])
    __app.add_url_rule("/todos/edit/<int:todo_id>", "editPage", __edit_task_page, methods=["GET"])
    __app.add_url_rule("/todos/new/task", "createTask", __create_task, methods=["POST"])
    __app.add_url_rule("/todos/edit/<int:todo_id>", "editTask", __edit_task, methods=["POST"])
    __app.add_url_rule("/todos/filter", "filter", __filter_task, methods=["GET"])
    __app.add_url_rule("/todos/style", "style", __generate_style, methods=["GET"])
    __app.add_url_rule("/todos/delete/<int:todo_id>", "deletePage", __delete_task_page, methods=["GET"])
    __app.add_url_rule("/todos/delete/<int:todo_id>", "deleteTask", __delete_task, methods=["POST"])
    __app.add_url_rule("/todos/habitReport", "habitReport", __habit_report, methods=["GET"])

    __app.add_url_rule("/categories/new/category", "newCategory", __load_category_new_page, methods=["GET"])
    __app.add_url_rule("/categories/new/category", "createCategory", __create_category, methods=["POST"])
    __app.add_url_rule("/todos/plan", "plan", __generate_todo_plan, methods=["GET"])
    __app.add_url_rule("/todos/thermalPrintImage","thermalPrintImage", __generate_thermal_print_image, methods=["GET"])

    __app.add_url_rule("/todos/manage/<int:todo_id>", "manageHabitTaskPage", __manage_habit_task_page, methods=["GET"])
    __app.add_url_rule("/todos/manage/<int:todo_id>", "manageHabitTask", __manage_habit_task, methods=["POST"])

def __generate_style():
    resp = make_response(render_template("style.css", commons=commons, categories=__database.get_categories()))
    resp.headers['Content-Type'] = 'text/css'
    return resp


def __filter_task():
    return render_template("filter.html", commons=commons, categories=__database.get_categories())


# routes
def __habit_report():
    month = request.args.get("month")
    year = request.args.get("year")
    start_date = datetime(int(year), int(month), 1,0,0,0,0, tzinfo=task_utils.__get_ui_time_zone()).astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    if int(month) != 12:
        end_date = (datetime(int(year), int(month)+1, 1, tzinfo=task_utils.__get_ui_time_zone()) + timedelta(days=-1))
    else:
        end_date = (datetime(int(year)+1, 1, 1, tzinfo=task_utils.__get_ui_time_zone()) + timedelta(days=-1))

    end_day = end_date.day
    end_date = end_date.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    todo_logs_entry = __database.get_todo_logs(start_date, end_date)
    todo_logs_entry_by_id = task_utils.get_task_logs_entry_by_id(todo_logs_entry)
    return render_template("habitReport.html", entries=todo_logs_entry_by_id, month=month, year=year, start_day=1, end_day=end_day)

def __delete_task(todo_id):
    __database.delete_todo(todo_id)
    return redirect(url_for("home"), 302)

def __edit_task(todo_id):
    formData = request.form
    data = commons.validateCreateEditPayload(formData, todo_id)
    if "globalErrors" in data:
        return __edit_task_page(todo_id, data)
    check_type(data, TodoUpdatePayload)
    __database.upsert_todo(todo_id, data)
    return redirect(url_for("home"), 302)


def __create_task():
    formData = request.form
    data: TodoCreatePayload = commons.validateCreateEditPayload(formData)
    if "globalErrors" in data:
        return __load_create_new_page(data)
    check_type(data, TodoCreatePayload)
    __database.create_todo(data)
    return redirect(url_for("home"), 302)


def __edit_task_page(todo_id, errors=None):
    todo = __database.get_todo(todo_id)
    return render_template("editCreateTask.html",
                           data={"action": "edit",
                                 "taskData": todo and task_utils.get_task_view_model(todo, {}, request.accept_languages),
                                 "errors": errors, "commons": commons, "categories":__database.get_categories()})

def __delete_task_page(todo_id, errors=None):
    todo = __database.get_todo(todo_id)
    return render_template("deleteTask.html", data={"action": "delete",
                                                    "taskData": todo and task_utils.get_task_view_model(todo, {}, request.accept_languages)})


def __load_create_new_page(errors=None):
    return render_template("editCreateTask.html", data={"action": "create", "taskData": None, "errors": errors, "commons": commons, "categories":__database.get_categories()}), 422 if errors else 200

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
    return render_template("homepage.html", todos=todos_by_type, errors=errors, filterString=filterString, commons=commons, partitions=["ALERTS", "PENDING", "TODAY", "UPCOMING"], till=till, groupBy=groupBy, currentMonthYear=task_utils.get_current_month_year(), categories=__database.get_categories())

def __group_by_slots(allTodos, todo_logs_map, errors, filterString, till, groupBy):
    todos_by_slot = {}
    
    for slot in commons.slots:
        todos_by_slot[commons.slots[slot]] = []
    
    for todo in allTodos:
        check_type(todo, Todo)
        if "timeSlot" not in todo or todo["timeSlot"] is None:
            todos_by_slot[commons.slots["None"]].append(task_utils.get_task_view_model(todo, todo_logs_map, request.accept_languages))
        else:
            todos_by_slot[commons.slots[str(todo["timeSlot"])]].append(task_utils.get_task_view_model(todo, todo_logs_map, request.accept_languages))

    return render_template("homepage.html", todos=todos_by_slot, errors=errors, filterString=filterString, commons=commons, partitions=commons.slots.values(), till=till, groupBy=groupBy, currentMonthYear=task_utils.get_current_month_year(), categories=__database.get_categories())

def __home_page(errors=None):
    filterString = ""
    if request.args.get("query"):
        filters = __database.parseFilters(request.args.get("query"))
        if filters:
            filterString = request.args.get("query")
    else:
        filters = []

    if request.args.get("till") and request.args.get("till") == "today":
        current_date = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC")).astimezone(task_utils.__get_ui_time_zone()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
        allTodos: List[Todo] = __database.get_all_todos_before_date(filters, ["due_date"], current_date)
    elif request.args.get("till") and request.args.get("till") == "this_month":
        current_date = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC")).astimezone(task_utils.__get_ui_time_zone()).replace(hour=23, minute=59, second=59, microsecond=0).astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
        current_date = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])
        allTodos: List[Todo] = __database.get_all_todos_before_date(filters, ["due_date"], current_date)
    else:    
        allTodos: List[Todo] = __database.get_all_todos_by_due_date(filters)
    todo_logs: TodoLog = __database.get_todo_logs_count()
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
    errors: PayloadError = {"globalErrors": []}
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
        todo_data: TodoTaskDoneOrSkipModel = {'due_date': due_date, 'todo_action': data['done_or_skip'], 'todo_id': int(dataKey)}
        check_type(todo_data, TodoTaskDoneOrSkipModel)
        __database.process_todo_action(todo_data)
    return __home_page()


def __load_category_new_page(errors=None):
    return render_template("editCreateCategory.html", data={"errors": errors, "categories": __database.get_categories()})


def __create_category():
    formData = request.form
    data: CategoryCreateEditPayload = commons.validateCreateEditCategoryPayload(formData)
    if "globalErrors" in data:
        return __load_category_new_page(data)
    check_type(data, CategoryCreateEditPayload)
    try:
        __database.create_category(data)
    except Exception as e:
        return __load_category_new_page({"globalErrors":[str(e)]})
    return redirect(url_for("home"), 302)


def __generate_todo_plan_task_list(startDate, endDate):

    tasks = {}
    currentDate = startDate.replace() # cloning
    while currentDate <= endDate:
        tasks[currentDate] = {}
        for slot in commons.slots:
            tasks[currentDate][slot]=[]
        currentDate = currentDate + timedelta(days=1)

    data = __database.get_all_todos_by_due_date(None)
    for todo in data:
        
        if todo["due_date"]:
            todo_due_date_local = todo["due_date"].replace(tzinfo=ZoneInfo("UTC")).astimezone(task_utils.__get_ui_time_zone())
        else:
            todo_due_date_local = datetime.now(ZoneInfo("UTC")).astimezone(task_utils.__get_ui_time_zone())
        
        todo_due = todo_due_date_local.date()

        if todo_due >= startDate and todo_due <= endDate:
            tasks[todo_due][str(todo["timeSlot"])].append(todo)

        frequency_model = recur.parse_frequency(todo["frequency"])
        if frequency_model:           
            next_due_date = recur.get_next_occurrence(frequency_model, todo_due_date_local)

            while next_due_date.date() <= endDate:
                if next_due_date.date() >= startDate:
                    tasks[next_due_date.date()][str(todo["timeSlot"])].append(todo)
                todo_due_date_local = next_due_date
                next_due_date = recur.get_next_occurrence(frequency_model, todo_due_date_local)
    return tasks

def __generate_todo_plan():
    
    startDateFromRequest  = request.args.get("startDate")
    endDateFromRequest = request.args.get("endDate")

    startDate = date.today() if startDateFromRequest is None else datetime.strptime(startDateFromRequest, "%Y-%m-%d").date()
    endDate = startDate + timedelta(days=6) if endDateFromRequest is None else datetime.strptime(endDateFromRequest, "%Y-%m-%d").date()

    dayOfWeekMapping={}
    currentDate = startDate.replace() # cloning
    while currentDate <= endDate:
        dayOfWeekMapping[currentDate] = calendar.day_name[currentDate.weekday()]
        currentDate = currentDate + timedelta(days=1)


    tasks = __generate_todo_plan_task_list(startDate, endDate)    
    return render_template("plan.html", data={"tasks": tasks, "slots": commons.slots, "dayOfWeekMapping":dayOfWeekMapping})

def __generate_thermal_print_image():
    startDateFromRequest  = request.args.get("startDate")

    startDate = date.today() if startDateFromRequest is None else datetime.strptime(startDateFromRequest, "%Y-%m-%d").date()
    taskList = __generate_todo_plan_task_list(startDate, startDate)

    finalTaskList = []
    for slot in taskList[startDate]:
        for task in taskList[startDate][slot]:
            finalTaskList.append(task["task"])

    return send_file(thermalPrintImageGenerator.create_image_from_list(calendar.day_name[startDate.weekday()][0:3] + ":" + startDate.strftime("%Y-%m-%d")
 ,finalTaskList), mimetype="image/png", as_attachment=True, download_name="today.png")



def __manage_habit_task_page(todo_id):
    todo = __database.get_todo(todo_id)
    taskOccurences = task_utils.get_all_occurrences_till_today_with_next(todo)
    return render_template("manageHabitTask.html",
                           data={"taskData": todo and task_utils.get_task_view_model(todo, {}, request.accept_languages),
                                 "errors": "", "occurrences": taskOccurences,
                                 "till": request.args.get("till"), "groupBy": request.args.get("groupBy"),
                                 "filterString": request.args.get("query")
                                 })

def __manage_habit_task(todo_id):
    formData = request.form
    taskInputs = sorted(formData)
    todo = __database.get_todo(todo_id)
    print(taskInputs)
    for i in range(0, len(taskInputs)):
        if i == len(taskInputs) - 1:
            next_due = task_utils.get_next_occurrence_from_date_str(todo, taskInputs[i])
            todo_data: TodoTaskDoneOrSkipModel = {'due_date': next_due, 'todo_action': formData[taskInputs[i]], 'todo_id': int(todo_id)}
        else:
            todo_data: TodoTaskDoneOrSkipModel = {'due_date': datetime.utcfromtimestamp(task_utils.get_local_datetime_object(taskInputs[i+1]).timestamp()), 'todo_action': formData[taskInputs[i]], 'todo_id': int(todo_id)}
        check_type(todo_data, TodoTaskDoneOrSkipModel)
        print(todo_data)
        __database.process_todo_action(todo_data)
    queryParms=""
    if request.args.get("query"):
        queryParms = queryParms+"query="+request.args.get("query")
    if request.args.get("till"):
        queryParms = queryParms+"&till="+request.args.get("till")
    if request.args.get("groupBy"):
        queryParms = queryParms+"&groupBy="+request.args.get("groupBy")
    return redirect(url_for("home")+"?"+queryParms, 302)

