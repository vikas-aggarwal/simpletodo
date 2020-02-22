def getDataAccessObject(APP):
    #defaults
    APP.config['DB_TYPE'] = "sqlite3"
    APP.config['SQLITE3_DB_PATH'] = "simpleTodo.db"

    if APP.config['ENV'] == "automatedTesting":
        APP.config.from_pyfile("testing.py");
    else :
        APP.config.from_pyfile("production.py");
        
    if APP.config['DB_TYPE'] == "mongo":
        import simpleTodoDataAccessMongo
        TODO_DATA = simpleTodoDataAccessMongo.SimpleTodoDataAccessMongo(APP)
    elif APP.config['DB_TYPE'] == "sqlite3" :
        import simpleTodoDataAccessSqlite3
        TODO_DATA = simpleTodoDataAccessSqlite3.SimpleTodoDataAccessSqlite3(APP)
    else:
        raise ValueError("Invalid DB type")

    return TODO_DATA
