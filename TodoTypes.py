from typing_extensions import TypedDict
from typing import Optional
from datetime import datetime

Todo = TypedDict('Todo', {"todo_id": int, "due_date":datetime, "frequency":str, "task":str, "timeSlot":int, "trackHabit":bool,"remindBeforeDays":int})
TodoLog = TypedDict('TodoLog', {"todo_id": int, "count":int, "action":str,})
TodoUpdatePayload = TypedDict('TodoUpdatePayload', {"todo_id": int, "due_date":int, "frequency":str, "task":str, "timeSlot":int, "trackHabit":bool,"remindBeforeDays":int, "todo_action":Optional[str], "due_date_utc":datetime}
)
TodoLogDB = TypedDict('TodoLogDB', {"todo_id": int, "creation_timestamp":datetime, "action":Optional[str], "due_date":Optional[datetime]})
