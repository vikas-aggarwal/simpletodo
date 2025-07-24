from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from conf import testing

def before_all(context):
    firefox_bin = "/snap/firefox/current/usr/lib/firefox/firefox"
    firefoxdriver_bin = "/snap/firefox/current/usr/lib/firefox/geckodriver"
    service = webdriver.firefox.service.Service(executable_path=firefoxdriver_bin)
    options = webdriver.firefox.options.Options()
    #options.add_argument('--headless')
    options.binary_location = firefox_bin
    context.browser = webdriver.Firefox(options=options, service=service)
    context.wait = WebDriverWait(context.browser, 10)
    context.host = "localhost"
    context.port = "8080"
    context.protocol = "http"
    context.dateFormatForFeature = "%d-%b-%Y"
    context.dateFormatForInput = "%Y-%m-%d"
    context.dateFormatFromInputText = "%Y-%m-%d" #"%d/%m/%Y"  # TODO: Re-evaluate

def after_all(context):
    context.browser.quit()
    
def before_scenario(context, scenario):
    # Wipe database
    if testing.DB_TYPE == "mongo":
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client["automatedTesting"]
        db.todos.drop()
        db.todo_logs.drop()
        db.categories.drop()
        client.close()
    else:
        import sqlite3
        conn = sqlite3.connect(testing.SQLITE3_DB_PATH)
        db = conn.cursor()
        db.execute("delete from todos")
        db.execute("delete from todo_logs")
        db.execute("delete from categories where internal_name = 'testing'")
        conn.commit()
        conn.close()
