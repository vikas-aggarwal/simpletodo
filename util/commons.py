from ui import TaskUtils as task_utils
from zoneinfo import ZoneInfo
from TodoTypes import PayloadError, TodoUpdatePayload, CategoryCreateEditPayload
from typing import Union
import re

slots = {"1": "Post Wake up",
         "2": "Before Bath",
         "3": "Before Lunch",
         "4": "Post Tea",
         "5": "Before Dinner",
         "6": "Before Sleep",
         "None": "Anytime",}


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

def validateDuration(duration):
    if duration and (not duration.isdigit()):
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

    if(validateDuration(formData.get('duration')) is False):
        errors["globalErrors"].append("Invalid Duration. Should be a number")

    if len(errors["globalErrors"]) > 0:
        return errors

    data = {"due_date": None,
            "frequency": formData.get('frequency'),
            "task": formData.get('taskTitle'),
            "timeSlot": None,
            "remindBeforeDays": None,
            "trackHabit": formData.get("trackHabit") == "on",
            "category": formData.get("category"),
            "todo_id": todo_id,
            "description": formData.get('description'),
            "duration": None
            }  # type: TodoUpdatePayload

    if 'slot' in formData and formData['slot'] == "None":
        data['timeSlot'] = None
    elif 'slot' in formData:
        data['timeSlot'] = int(formData['slot'])

    if 'dueDate' in formData and formData['dueDate'] != "":
        data['due_date'] = task_utils.get_local_datetime_object(formData["dueDate"]).astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

    if formData.get("remindBeforeDays") and formData.get("remindBeforeDays") == "":
        data["remindBeforeDays"] = None
    elif formData.get("remindBeforeDays"):
        data["remindBeforeDays"] = int(formData.get("remindBeforeDays"))

    if formData.get("duration") and formData.get("duration") == "":
        data["duration"] = None
    elif formData.get("duration"):
        data["duration"] = int(formData.get("duration"))

    return data

def validateCreateEditCategoryPayload(formData) -> Union[PayloadError, CategoryCreateEditPayload]:
    errors = {"globalErrors": []}  # type: PayloadError

    if(formData.get("displayName") is None or re.fullmatch("[A-Z][a-z0-9]{2,10}", formData.get("displayName")) is None):
        errors["globalErrors"].append("Invalid Display Name")

    if(formData.get("internalName") is None or re.fullmatch("[a-z0-9]{3,11}", formData.get("internalName")) is None):
        errors["globalErrors"].append("Invalid Internal Name")

    if(formData.get("backgroundColor") is None or re.fullmatch("#[a-f0-9]{6}", formData.get("backgroundColor")) is None):
        errors["globalErrors"].append("Invalid Background Color")

    if len(errors["globalErrors"]) > 0:
        return errors

    data = {
        "internal_name": formData.get("internalName"),
        "display_name": formData.get("displayName"),
        "background_color": formData.get("backgroundColor")
    }  # type: CategoryCreateEditPayload

    return data
