from ui import TaskUtils as task_utils
import pytz
from TodoTypes import PayloadError, TodoUpdatePayload
from typing import Union

categories = {"uncategorized": "Uncategorized",
              "health": "Health",
              "finance": "Finance",
              "maintenance": "Maintenance",
              "bills": "Bills",
              "learning": "Learning"}

categoriesColorMap = {"uncategorized": "#ceecce",
                      "health": "#9eb0e3",
                      "finance": "#eae485",
                      "maintenance": "#e8bdbd",
                      "bills": "#A0CCDB",
                      "learning": "#d5af56"}

slots = {"None": "Anytime",
         "1": "Post Wake up",
         "2": "Before Bath",
         "3": "Before Lunch",
         "4": "Post Tea",
         "5": "Before Dinner",
         "6": "Before Sleep"}


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


def validateDueDate(dueDate):
    try:
        if dueDate:
            task_utils.get_local_datetime_object(dueDate).timestamp()
    except ValueError:
        return False
    return True


def validateCreateEditPayload(formData, todo_id=None) -> Union[PayloadError, TodoUpdatePayload]:
    errors = {"globalErrors": []}  # type: PayloadError

    if(__validateTimeSlot(formData.get("slot")) is False):
        errors["globalErrors"].append("Invalid Time Slot")

    if(__validateRemindBeforeDays(formData.get('remindBeforeDays')) is False):
        errors["globalErrors"].append("Remind before days should be a number")

    if(validateDueDate(formData.get('dueDate')) is False):
        errors["globalErrors"].append("Invalid Due Date. Format should be yyyy-MM-DD")

    if len(errors["globalErrors"]) > 0:
        return errors

    data = {"due_date": None,
            "frequency": formData.get('frequency'),
            "task": formData.get('taskTitle'),
            "timeSlot": None,
            "remindBeforeDays": None,
            "trackHabit": formData.get("trackHabit") == "on",
            "category": formData.get("category"),
            "todo_id": todo_id
            }  # type: TodoUpdatePayload

    if 'slot' in formData and formData['slot'] == "None":
        data['timeSlot'] = None
    elif 'slot' in formData:
        data['timeSlot'] = int(formData['slot'])

    if 'dueDate' in formData and formData['dueDate'] != "":
        data['due_date'] = task_utils.get_local_datetime_object(formData["dueDate"]).astimezone(pytz.UTC).replace(tzinfo=None)

    if formData.get("remindBeforeDays") and formData.get("remindBeforeDays") == "":
        data["remindBeforeDays"] = None
    elif formData.get("remindBeforeDays"):
        data["remindBeforeDays"] = int(formData.get("remindBeforeDays"))
    return data
