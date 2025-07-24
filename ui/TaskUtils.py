from TodoTypes import Todo
from TodoTypes import TodoListViewModel
from TodoTypes import TaskBuckets
from typing import List
from datetime import datetime
from datetime import timedelta
import pytz
from util import recur
from runtime_type_checker import check_type

date_format = '%Y-%m-%d'


def get_local_datetime_object(date_str):
    return __get_ui_time_zone().localize(datetime.strptime(date_str,
                                                           date_format))


def __get_ui_time_zone():
    # Returning default for now, will have a user preference layer in future
    return pytz.timezone("Asia/Kolkata")


def get_task_logs_entry_by_id(todo_logs_entry):
    entries = {}
    for log_entry in todo_logs_entry :
        todo_id = log_entry['todo_id']
        if todo_id not in entries:
            entries[todo_id]={"task":"", "logs": {}}
        entries[todo_id]["task"] = log_entry["task"]
        entries[todo_id]["logs"][pytz.utc.localize(log_entry["due_date"]).astimezone(__get_ui_time_zone()).day] = log_entry["action"]
    return entries
        
def get_task_bucket(todo: Todo) -> TaskBuckets:
    if todo['due_date'] is None:
        return TaskBuckets.TODAY
    currentTime = pytz.utc.localize(datetime.utcnow()
                                    ).astimezone(__get_ui_time_zone())
    todo_due_date_local = pytz.utc.localize(todo['due_date']
                                            ).astimezone(__get_ui_time_zone())
    if currentTime.date() == todo_due_date_local.date():
        return TaskBuckets.TODAY

    if currentTime.date() > todo_due_date_local.date():
        return TaskBuckets.PENDING

    if todo['remindBeforeDays'] is not None:
        if currentTime.date() >= (todo_due_date_local.date()
                                  - timedelta(todo['remindBeforeDays'])):
            return TaskBuckets.ALERTS

    return TaskBuckets.UPCOMING

def get_all_occurrences_till_today_with_next(todo: Todo):
    occurences = []
    currentTime = pytz.utc.localize(datetime.utcnow()).astimezone(__get_ui_time_zone())
    todo_due_date_local = pytz.utc.localize(todo['due_date']).astimezone(__get_ui_time_zone())
    occurences.append(todo_due_date_local.strftime(date_format))

    frequency_model = recur.parse_frequency(todo["frequency"])
    next_due_date = recur.get_next_occurrence(frequency_model, todo_due_date_local)
    while next_due_date <= currentTime:
        occurences.append(next_due_date.strftime(date_format))
        next_due_date = recur.get_next_occurrence(frequency_model, next_due_date)

    return occurences

def get_next_occurrence_from_date_str(todo: Todo, start_date: datetime):
    todo_due_date_local = datetime.utcfromtimestamp(get_local_datetime_object(start_date).timestamp())
    frequency_model = recur.parse_frequency(todo["frequency"])
    next_due_date = recur.get_next_occurrence(frequency_model, todo_due_date_local)
    return next_due_date

def get_task_view_model(todo: Todo, todo_logs_map, accept_languages) -> TodoListViewModel:
    todoModel = {"todo_id": todo['todo_id'],
                                    "due_date_str": "",
                                    "due_date": datetime.now(),  # To satisfy type system
                                    "frequency": todo['frequency'],
                                    "task": todo['task'],
                                    "trackHabit": todo['trackHabit'],
                                    "timeSlot": todo['timeSlot'],
                                    "remindBeforeDays": '',
                                    "next_due_date": None,  # TODO
                                    "due_in_days": None,
                                    "done_count": None,
                                    "skip_count": None,
                                    "category": todo['category'],
                                    "duration": todo['duration'],
                                    "description": todo['description']}  # type: TodoListViewModel
    if todo['task'] is None or todo['task'] == "":
        todoModel['task'] = "<No Title>"

    if(todo['due_date'] is None):
        todoModel['due_date'] = datetime.utcnow()
    else:
        todoModel['due_date'] = todo['due_date']

    currentTime = pytz.utc.localize(datetime.utcnow()).astimezone(__get_ui_time_zone())
    todo_due_date_local = pytz.utc.localize(todoModel['due_date']).astimezone(__get_ui_time_zone())

    todoModel["due_date_str"] = todo_due_date_local.strftime(date_format)

    todoModel['due_in_days'] = (todo_due_date_local.date() - currentTime.date()).days

    frequency_model = recur.parse_frequency(todo["frequency"])
    if frequency_model:
        if not todo["trackHabit"]:
            next_due_date = recur.get_next_occurrence_after(frequency_model, todo_due_date_local, currentTime)
        else:
            next_due_date = recur.get_next_occurrence(frequency_model, todo_due_date_local)

        if next_due_date:
            todoModel['next_due_date'] = next_due_date.strftime(date_format)
    if todo['remindBeforeDays']:
        todoModel['remindBeforeDays'] = str(todo['remindBeforeDays'])

    if todo["todo_id"] in todo_logs_map:
        todoModel["done_count"] = todo_logs_map[todo["todo_id"]].get("Done", 0)
        todoModel["skip_count"] = todo_logs_map[todo["todo_id"]].get("Skip", 0)
    elif todo["trackHabit"]:
        todoModel["done_count"] = 0
        todoModel["skip_count"] = 0
    check_type(todoModel, TodoListViewModel)
    return todoModel


def sort_task_by_slots(todos: List[TodoListViewModel]):
    todos.sort(key=lambda todo: (todo["timeSlot"] and ((todo["timeSlot"] == "None" and 9) or todo["timeSlot"])) or 9)


def get_current_month_year():
    currentTime = pytz.utc.localize(datetime.utcnow()).astimezone(__get_ui_time_zone())
    return [currentTime.month, currentTime.year]
