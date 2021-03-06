from datetime import timedelta, datetime
from TodoTypes import RecurrenceModel
from typing import Optional, Dict

def get_next_occurrence(recur: RecurrenceModel, start_date:datetime) -> Optional[datetime]:
    # start_date should be in the end users timezone for day of week to work correctly
    day_of_week_map = {"Sun": 7, "Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6}
    try:
        if recur["Frequency"] == "Day":
            return start_date + timedelta(days=recur["FrequencyCount"])
        if recur["Frequency"] == "Week":
            start_date = start_date + timedelta(weeks=recur["FrequencyCount"])
            if recur["Day_of_week"] is not None and start_date.isoweekday() != day_of_week_map[recur["Day_of_week"]]:
                expected_weekday = day_of_week_map[recur["Day_of_week"]] % 7
                actual_weekday = start_date.isoweekday() % 7
                diff_in_days = expected_weekday - actual_weekday
                if diff_in_days < 0:
                    diff_in_days = 7 + diff_in_days
                start_date = start_date + timedelta(days=diff_in_days)
            return start_date
        if recur["Frequency"] == "Month":
            to_month = start_date.month + recur["FrequencyCount"]
            to_year = start_date.year
            if to_month > 12:
                to_year = to_year + 1
                to_month = to_month % 12
            return start_date.replace(year=to_year, month=to_month)
        if recur["Frequency"] == "Year":
            to_year = start_date.year + recur["FrequencyCount"]
            try:
                start_date = start_date.replace(year=to_year)
            except ValueError:
                start_date = start_date + timedelta(days=-1)  # Feb 29th
                start_date = start_date.replace(year=to_year)
            return start_date
    except:
        pass
    return None


def parse_frequency(frequencyString:str) -> Optional[RecurrenceModel]:
    if frequencyString:
        frequencyString = frequencyString.lower()
        components = frequencyString.split()

        if len(components) == 1:
            simpleFreq = {
                "daily": {"Frequency": "Day", "FrequencyCount": 1, "Day_of_week" : None},
                "monday": {"Frequency" : "Week","FrequencyCount" : 1,"Day_of_week" : "Mon"},
                "tuesday":{"Frequency" : "Week","FrequencyCount" : 1,"Day_of_week" : "Tue"},
                "wednesday": {"Frequency" : "Week","FrequencyCount" : 1,"Day_of_week" : "Wed"},
                "thursday":{"Frequency" : "Week","FrequencyCount" : 1,"Day_of_week" : "Thu"},
                "friday":{"Frequency" : "Week","FrequencyCount" : 1,"Day_of_week" : "Fri"},
                "saturday":{"Frequency" : "Week","FrequencyCount" : 1,"Day_of_week" : "Sat"},
                "sunday":{"Frequency" : "Week","FrequencyCount" : 1,"Day_of_week" : "Sun"},
                "monthly":{"Frequency" : "Month","FrequencyCount" : 1, "Day_of_week" : None},
                "weekly":{"Frequency" : "Week","FrequencyCount" : 1, "Day_of_week" : None},
                "yearly":{"Frequency" : "Year","FrequencyCount" : 1, "Day_of_week" : None}
            }  # type: Dict[str, RecurrenceModel]
            if components[0] in simpleFreq:
                return simpleFreq[components[0]]
        elif len(components) == 3:
            if components[0] == "every":
                try:
                    if isinstance(int(components[1]), int):
                        x = ["week","weeks", "month",  "months" ,"year" , "years" , "day" , "days"];
                        if components[2] in x:
                            if components[2][0] == 'w':
                                return {"Frequency" : "Week",
                                        "FrequencyCount" : int(components[1]),
                                        "Day_of_week" : None
                                        }
                            elif components[2][0] == 'y':
                                return {"Frequency" : "Year",
                                        "FrequencyCount" : int(components[1]),
                                        "Day_of_week" : None
                                        }   
                            elif components[2][0] == 'd':
                                return {"Frequency" : "Day",
                                        "FrequencyCount" : int(components[1]),
                                        "Day_of_week" : None
                                        }
                            elif components[2][0] == 'm':
                                return {"Frequency" : "Month",
                                        "FrequencyCount" : int(components[1]),
                                        "Day_of_week" : None
                                        }
                except:
                    pass 
    return None;
