from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pymongo

def before_all(context):
        #Wipe database
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client["automatedTesting"];
        db.todos.drop();
        db.todo_logs.drop();
        context.browser = webdriver.Firefox();
        context.wait    = WebDriverWait(context.browser, 10)

def after_all(context):
	context.browser.quit()
