import sqlite3

def __is_new_database(conn):
    db = conn.cursor()
    db.execute("select name from sqlite_master where type='table'")
    rows = db.fetchall()
    db.close()
    if len(rows) == 0:
        return True

def __create_version_table_if_does_not_exists(conn):
    conn.execute('''
    CREATE TABLE if not exists todo_schema_version (
    version integer
)
    ''')


def __create_tables(conn):
    conn.execute('''
    CREATE TABLE if not exists todos(
    todo_id integer,
    due_date text,
    frequency text,
    remind_before_days integer,
    task_name text,
    time_slot integer,
    todo_action text,
    track_habit integer,
    category text
    )
    ''')

    conn.execute('''
    CREATE TABLE if not exists todo_logs (
    todo_id integer,
    action text,
    due_date text,
    creation_timestamp text
    )
    ''')

def __get_current_schema_version(conn):
    __create_version_table_if_does_not_exists(conn)
    db = conn.cursor()
    db.execute("select version from todo_schema_version")
    row = db.fetchone()
    if row:
        version = row['version']
    else:
        version = 0
    db.close()
    return version

def __set_version_on_database(conn, schema_version):
    db = conn.cursor()
    db.execute("select version from todo_schema_version")
    if db.fetchone():
        db.execute("update todo_schema_version set version = ?", (schema_version, ))
    else:
        db.execute("insert into todo_schema_version (version) VALUES (?)", (schema_version, ))
    db.close()

def __get_columns_for_table_csv(conn, table):
    columns = []
    db = conn.cursor()
    db.execute("select name from pragma_table_info('" + table + "')")
    rows = db.fetchall()
    for r in rows:
        columns.append(r['name'])
    db.close()
    return ",".join(columns)

def process(conn: sqlite3.Connection, schema_version):
    if __is_new_database(conn):
        print("New Database detected")
        __create_tables(conn)
        __create_version_table_if_does_not_exists(conn)
        __set_version_on_database(conn, schema_version)
        version = schema_version
    else:  # Table should exists
        version = __get_current_schema_version(conn)
        if version < schema_version:  # Upgrade
            print("Older version detected, updating from " + str(version) + " to " + str(schema_version));
            db = conn.cursor()
            db.execute("alter table todos rename to todos_temp")
            db.execute("alter table todo_logs rename to todo_logs_temp")
            __create_tables(conn)
            todos_temp_column = __get_columns_for_table_csv(conn, 'todos_temp')
            db.execute("insert into todos (" + todos_temp_column + ") select " + todos_temp_column + " from todos_temp")
            todo_logs_temp_column = __get_columns_for_table_csv(conn, 'todo_logs_temp')
            db.execute("insert into todo_logs (" + todo_logs_temp_column + ") select " + todo_logs_temp_column + " from todo_logs_temp")
            db.execute("drop table todos_temp")
            db.execute("drop table todo_logs_temp")
            __set_version_on_database(conn, schema_version)
            version = schema_version;
            db.close()
            conn.commit()
    if version == 2:  # run data fixes, version 2 has no schema changes, bumped up to run fixes
        db = conn.cursor()
        print("NULL data fix")
        db.execute("update todos set time_slot = NULL where time_slot = 'None'")
        db.execute("update todos set remind_before_days = NULL where remind_before_days = ''")
        db.close()
        conn.commit()
