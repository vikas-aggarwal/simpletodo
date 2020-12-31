from abc import ABCMeta, abstractmethod
from TodoTypes import Todo, TodoTaskDoneOrSkipModel, TodoUpdatePayload, TodoCreatePayload, FilterModel, FilterUnitModel

class DBManager(metaclass=ABCMeta):

    @abstractmethod
    def get_todo(self, todo_id) -> Todo:
        pass

    @abstractmethod
    def create_todo(self, data: TodoCreatePayload, todo_id):
        pass

    @abstractmethod
    def process_todo_action(self, data: TodoTaskDoneOrSkipModel):
        pass

    @abstractmethod
    def get_all_todos_by_due_date(self, filters):
        pass

    def _getSupportedOperators(self):
        return ["=", "!=", "LIKE"]

    def _getSupportedAttributes(self):
        return ["frequency", "trackHabit", "task", "category"]

    def _isSupportedAttribute(self, attribute):
        return attribute in self._getSupportedAttributes()

    def _isSupportedOperator(self, operator):
        return operator in self._getSupportedOperators()

    def getSchemaVersion(self):
        return 1

    def parseFilters(self, filters):
        '''
        Format filter=attribute=value;attribute!=value;attributeLIKEvalue
        Semicolon seperated.
        '''
        parsedFilter = []
        print("Parsing " + str(filters))
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
                        parsedFilter.append(parsedUnit)
                        unitParsed = True
            if unitParsed is False:
                return []
        return parsedFilter


def getDataAccessObject(APP):
    # defaults
    APP.config['DB_TYPE'] = "sqlite3"
    APP.config['SQLITE3_DB_PATH'] = "simpleTodo.db"

    if APP.config['ENV'] == "automatedTesting":
        APP.config.from_pyfile("conf/testing.py")
    else:
        APP.config.from_pyfile("conf/production.py")

    if APP.config['DB_TYPE'] == "mongo":
        import db.mongo.simpleTodoDataAccessMongo as simpleTodoDataAccessMongo 
        TODO_DATA = simpleTodoDataAccessMongo.SimpleTodoDataAccessMongo(APP)
    elif APP.config['DB_TYPE'] == "sqlite3":
        import db.sqlite.simpleTodoDataAccessSqlite3 as simpleTodoDataAccessSqlite3
        TODO_DATA = simpleTodoDataAccessSqlite3.SimpleTodoDataAccessSqlite3(APP)
    else:
        raise ValueError("Invalid DB type")

    return TODO_DATA
