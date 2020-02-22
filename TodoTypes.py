from typing_extensions import TypedDict

Todo = TypedDict('Todo', {"todo_id": int, "due_date":int, "frequency":str, "task":str, "timeSlot":int, "trackHabit":bool,"remindBeforeDays":int})
TodoLog = TypedDict('TodoLog', {"todo_id": int, "count":int, "action":str,})
