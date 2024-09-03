from typing_extensions import TypedDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


Category = TypedDict('Category', {"internal_name": str,
                                  "display_name": str,
                                  "background_color": str})

Todo = TypedDict('Todo', {"todo_id": int,
                          "due_date": Optional[datetime],
                          "frequency": Optional[str],
                          "task": str,  # Default to some string
                          "timeSlot": Optional[int],
                          "trackHabit": Optional[bool],
                          "category": Optional[str],
                          "remindBeforeDays": Optional[int]})

TodoLog = TypedDict('TodoLog', {"todo_id": int,
                                "count": int,
                                "action": str})

TodoLogEntry = TypedDict('TodoLogEntry', {"task": str,
                                          "due_date": datetime,
                                          "action": str,
                                          "todo_id": int
                                          })

TodoCreatePayload = TypedDict('TodoCreatePayload', {"todo_id": Optional[int],
                                                    "due_date": Optional[datetime],
                                                    "frequency": Optional[str],
                                                    "task": Optional[str],
                                                    "timeSlot": Optional[int],
                                                    "trackHabit": Optional[bool],
                                                    "category": Optional[str],
                                                    "remindBeforeDays": Optional[int]
                                                    })

TodoUpdatePayload = TypedDict('TodoUpdatePayload', {"todo_id": int,
                                                    "due_date": Optional[datetime],
                                                    "frequency": Optional[str],
                                                    "task": Optional[str],
                                                    "timeSlot": Optional[int],
                                                    "category": Optional[str],
                                                    "trackHabit": Optional[bool],
                                                    "remindBeforeDays": Optional[int]
                                                    })

TodoLogDB = TypedDict('TodoLogDB', {"todo_id": int,
                                    "creation_timestamp": datetime,
                                    "action": str,
                                    "due_date": Optional[datetime]})

TodoListViewModel = TypedDict('TodoListViewModel', {"todo_id": int,
                                                    "due_date": datetime,
                                                    "frequency": Optional[str],
                                                    "task": str,
                                                    "timeSlot": Optional[int],
                                                    "trackHabit": Optional[bool],
                                                    "due_date_str": str,
                                                    "category": Optional[str],
                                                    "remindBeforeDays": Optional[str],
                                                    "next_due_date": Optional[str],
                                                    "due_in_days": Optional[int],
                                                    "done_count": Optional[int],
                                                    "skip_count": Optional[int]})

TodoTaskDoneOrSkipModel = TypedDict('TodoTaskDoneOrSkipModel', {"todo_id": int,
                                                                "todo_action": str,
                                                                "due_date": datetime})

PayloadError = TypedDict('PayloadError', {"globalErrors": List[str]
                                          })

class TaskBuckets(Enum):
    ALERTS = "alert"
    PENDING = "pending"
    TODAY = "today"
    UPCOMING = "upcoming"


FilterUnitModel = TypedDict('FilterUnitModel', {"attribute": str,
                                        "operator":str,
                                        "value":str
                                          })

FilterModel = List[FilterUnitModel]

RecurrenceModel = TypedDict('RecurrenceModel', {"Frequency": str,
                                                "FrequencyCount": int,
                                                "Day_of_week": Optional[str]
                                                })
