from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from conf import testing
import datetime
import os

def before_all(context):
    context.browser = webdriver.Firefox()
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
        client.close()
    else:
        import sqlite3
        conn = sqlite3.connect(testing.SQLITE3_DB_PATH)
        db = conn.cursor();
        db.execute("delete from todos")
        db.execute("delete from todo_logs")
        conn.commit()
        conn.close()
