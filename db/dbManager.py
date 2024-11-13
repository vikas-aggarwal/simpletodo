from abc import ABCMeta, abstractmethod
from TodoTypes import Todo, TodoTaskDoneOrSkipModel, TodoUpdatePayload, TodoCreatePayload, FilterModel, FilterUnitModel, Category
from typing import Union, List
import os

class DBManager(metaclass=ABCMeta):

    @abstractmethod
    def get_categories(self) -> dict[str, Category]:
        pass
    
    @abstractmethod
    def get_todo(self, todo_id: int) -> Todo:
        pass

    @abstractmethod
    def create_todo(self, data: TodoCreatePayload, todo_id):
        pass

    @abstractmethod
    def upsert_todo(self, todo_id, data: TodoUpdatePayload):
        pass

    @abstractmethod
    def process_todo_action(self, data: TodoTaskDoneOrSkipModel):
        pass

    @abstractmethod
    def get_all_todos_by_due_date(self, filters):
        pass

    @abstractmethod
    def get_all_todos_before_date(self, filters, sort_criteria, current_date):
        pass

    @abstractmethod
    def delete_todo(self, todo_id):
        pass

    @abstractmethod
    def get_todo_logs(self, startTimeStamp, endTimeStamp):
        pass
    
    def _getSupportedOperators(self) -> List[str]:
        return ["=", "!=", "LIKE", "IN"]

    def _getSupportedAttributes(self) -> List[str]:
        return ["frequency", "trackHabit", "task", "category", "timeSlot"]

    def _isSupportedAttribute(self, attribute):
        return attribute in self._getSupportedAttributes()

    def _isSupportedOperator(self, operator):
        return operator in self._getSupportedOperators()

    def getSchemaVersion(self):
        return 3

    def parseFilters(self, filters) -> FilterModel:
        '''
        Format filter=attribute=value;attribute!=value;attributeLIKEvalue
        Semicolon seperated.
        '''
        parsedFilter = []

        for unit in filters.split(";"):
            unitParsed = False
            parsedUnit = {"attribute": "",
                          "operator": "",
                          "value": ""}  # type: FilterUnitModel
            for op in self._getSupportedOperators():
                if op in unit:
                    parsedUnit['operator'] = op
                    attributeValue = unit.split(op)
                    if len(attributeValue) == 2 and attributeValue[0] in self._getSupportedAttributes():
                        parsedUnit['attribute'] = attributeValue[0]
                        parsedUnit['value'] = attributeValue[1]
                        if op == "IN":
                            parsedUnit['value'] = parsedUnit['value'].split(",")
                        parsedFilter.append(parsedUnit)
                        unitParsed = True
            if unitParsed is False:
                return []
        return parsedFilter


def getDataAccessObject(APP):
    # defaults
    APP.config['DB_TYPE'] = "sqlite3"
    APP.config['SQLITE3_DB_PATH'] = "simpleTodo.db"

    if "automatedTesting" in os.environ:
        print("Automated Testing Mode")
        APP.config.from_pyfile("conf/testing.py")
    else:
        APP.config.from_pyfile(os.getcwd()+"/conf/production.py")

    if APP.config['DB_TYPE'] == "mongo":
        import db.mongo.simpleTodoDataAccessMongo as simpleTodoDataAccessMongo
        TODO_DATA = simpleTodoDataAccessMongo.SimpleTodoDataAccessMongo(APP)
    elif APP.config['DB_TYPE'] == "sqlite3":
        import db.sqlite.simpleTodoDataAccessSqlite3 as simpleTodoDataAccessSqlite3
        TODO_DATA = simpleTodoDataAccessSqlite3.SimpleTodoDataAccessSqlite3(APP)
    else:
        raise ValueError("Invalid DB type")

    return TODO_DATA
