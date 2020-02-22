from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import testing
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
    context.dateFormatFromInputText = "%d/%m/%Y"  # For GB locale

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
        

def after_scenario(context, scenario):
    coverage_data = context.browser.execute_script('return JSON.stringify(window.__coverage__ || {})')
    file_numbers = [int(x[x.index('_')+1:x.index('.json')]) for x  in  os.listdir('.') if x.startswith("jsCoverage_")]
    file_numbers.sort(reverse=True)
    if len(file_numbers) == 0 :
        file_number = 1
    else:
        file_number = file_numbers[0]+1
    coverage_file = open("jsCoverage_"+str(file_number)+".json","w")
    coverage_file.write(coverage_data)
    coverage_file.close()
