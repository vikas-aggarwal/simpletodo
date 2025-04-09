import sqlite3

def __is_new_database(conn):
    db = conn.cursor()
    db.execute("select name from sqlite_master where type='table'")
    rows = db.fetchall()
    db.close()
    if len(rows) == 0:
        return True


def __create_categories_seed_data_if_does_not_exists(conn):
    db = conn.cursor()
    db.execute("select internal_name from categories")
    rows = db.fetchall()
    if len(rows) == 0:
        db.execute("insert into categories(internal_name, display_name, background_color) values('uncategorized', 'Uncategorized', '#ceecce')")
        db.execute("insert into categories(internal_name, display_name, background_color) values('health', 'Health', '#9eb0e3')")
        db.execute("insert into categories(internal_name, display_name, background_color) values('finance', 'Finance','#eae485')")
        db.execute("insert into categories(internal_name, display_name, background_color) values('maintenance', 'Maintenance', '#e8bdbd')")
        db.execute("insert into categories(internal_name, display_name, background_color) values('bills', 'Bills', '#A0CCDB')")
        db.execute("insert into categories(internal_name, display_name, background_color) values('learning', 'Learning', '#d5af56')")
    db.close()
    conn.commit()
    
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
    category text,
    duration integer,
    description integer
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

    conn.execute('''
    CREATE TABLE if not exists categories (
    internal_name text,
    display_name text,
    background_color text
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

def __alter_todos_table(conn: sqlite3.Connection):
    conn.execute('''alter table todos add column duration integer''')
    conn.execute('''alter table todos add column description text''')

def process(conn: sqlite3.Connection, schema_version):
    if __is_new_database(conn):
        print("New Database detected")
        __create_tables(conn)
        __create_version_table_if_does_not_exists(conn)
        __create_categories_seed_data_if_does_not_exists(conn)
        __set_version_on_database(conn, schema_version)
        conn.commit()
        version = schema_version
    else:  # Table should exists
        version = __get_current_schema_version(conn)
        if version == 3:
            print("Upgrading database")
            __create_tables(conn)
            __alter_todos_table(conn) #for version 4 only
            __create_version_table_if_does_not_exists(conn)
            __create_categories_seed_data_if_does_not_exists(conn)
            __set_version_on_database(conn, schema_version)
            conn.commit()
        elif version != schema_version:
            raise Exception("Invalid Database version detected")
