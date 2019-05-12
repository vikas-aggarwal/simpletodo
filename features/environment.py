from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pymongo

def before_all(context):
        context.browser = webdriver.Firefox();
        context.wait    = WebDriverWait(context.browser, 10)
        context.host    = "localhost"
        context.port    = "8080"
        context.protocol= "http"
        context.dateFormatForFeature = "%d-%b-%Y"
        context.dateFormatForInput = "%Y-%m-%d"
        context.dateFormatFromInputText = "%m/%d/%Y" #For US locale

def after_all(context):
	context.browser.quit()

def before_scenario(context, scenario):
        #Wipe database
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client["automatedTesting"];
        db.todos.drop();
        db.todo_logs.drop();
        client.close();
