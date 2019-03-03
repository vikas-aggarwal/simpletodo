from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

def before_all(context):
        context.browser = webdriver.Firefox();
        context.wait    = WebDriverWait(context.browser, 10)

def after_all(context):
	context.browser.quit()
