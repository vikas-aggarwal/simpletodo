import json
import http
import datetime
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from behave import *
from assertpy import *
import selenium

def create_task(payload,host,port):
    http_client = http.client.HTTPConnection(host, port)
    http_client.request("POST", "/todos", json.dumps(payload), {'Content-Type':'application/json'})
    response = http_client.getresponse()
    assert_that(response.status).is_equal_to(200)
    return json.load(response)['todo_id']

def create_task_log(payload,todo_id,host,port):
    http_client = http.client.HTTPConnection(host, port)
    http_client.request("POST", "/todos/"+str(todo_id), json.dumps(payload), {'Content-Type':'application/json'})
    response = http_client.getresponse()
    assert_that(response.status).is_equal_to(200)




@when(u'user already has a non-habit task "{taskName}" with frequency "{frequency}" and due date as "{dueDate}"')
def step_impl(context, taskName, frequency, dueDate):
    payload = {}
    payload['frequency'] = frequency
    payload['task'] = taskName
    payload['due_date'] = datetime.datetime.strptime(dueDate, context.dateFormatForFeature).timestamp()
    todo_id = create_task(payload, context.host, context.port)
    context.current_todo_id = todo_id
    context.browser.find_element(By.ID, "refreshData").click();
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")))


@when(u'user already has a habit task "{taskName}" with frequency "{frequency}" and due date as "{dueDate}" with count "{count}"')
def step_impl(context, taskName, frequency, dueDate, count):
    payload = {}
    payload['frequency'] = frequency
    payload['task'] = taskName
    payload['trackHabit'] = "true"
    payload['due_date'] = datetime.datetime.strptime(dueDate, context.dateFormatForFeature).timestamp()
    todo_id = create_task(payload, context.host, context.port)
    last_due_date = payload['due_date']
    context.current_todo_id = todo_id
    for i in range(0, int(count)):
        payload = {}
        payload['due_date'] = (datetime.datetime.fromtimestamp(last_due_date) + datetime.timedelta(days=1)).timestamp()
        last_due_date = payload['due_date']
        payload['todo_action'] = 'Done'
        payload['todo_id'] = todo_id
        create_task_log(payload, todo_id, context.host, context.port)

        payload = {}
        payload['due_date'] = (datetime.datetime.fromtimestamp(last_due_date) + datetime.timedelta(days=1)).timestamp()
        last_due_date = payload['due_date']
        payload['todo_action'] = 'Skip'
        payload['todo_id'] = todo_id
        create_task_log(payload, todo_id, context.host, context.port)

    context.browser.find_element(By.ID, "refreshData").click();
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")))



@when(u'user marks the task "{taskName}" as "{action}"')
def step_impl(context, taskName, action):
    task_node = context.browser.find_element(By.XPATH, "//li[//h3[text()='"+taskName+"']]")
    action_button = task_node.find_element(By.XPATH, "//button[contains(text(),'"+action+"')]")
    action_button.click()
    context.actionButton = action_button

@then(u'the due date of the task "{taskName}" should change to "{newDueDate}"')
def step_impl(context, taskName, newDueDate):
    task_node = context.browser.find_element(By.XPATH, "//li[//h3[text()='"+taskName+"']]")  # type: selenium.webdriver.remote.webelement.WebElement
    due_date = task_node.find_element(By.XPATH, "//*[contains(@id,'label_due')]").text
    due_date_to_verify = datetime.datetime.strptime(due_date, context.dateFormatFromInputText).strftime(context.dateFormatForFeature)
    assert_that(due_date_to_verify).is_equal_to(newDueDate)



@then(u'Done button should be disabled')
def step_impl(context):
    button = context.actionButton # type: selenium.webdriver.remote.webelement.WebElement
    assert_that("ui-state-disabled" in button.get_attribute("class")).is_true()




@when(u'user selects a next due date as "{newDueDate}" as the done button is disabled')
def step_impl(context, newDueDate):
    driver = context.browser # type: selenium.webdriver.Firefox
    current_todo_id = context.current_todo_id
    button = driver.find_element(By.XPATH, '//li[@data-region-id="'+str(current_todo_id)+'_region"]//button[contains(text(),"Done")]')
    assert_that("ui-state-disabled" in button.get_attribute("class")).is_true()
    newDueDateInISOFormat = datetime.datetime.strptime(newDueDate, context.dateFormatForFeature).strftime(context.dateFormatForInput)
    driver.find_element(By.ID, str(current_todo_id)+"_date").send_keys(newDueDateInISOFormat)
    context.wait.until(EC.element_to_be_clickable((By.XPATH ,'//li[@data-region-id="'+str(current_todo_id)+'_region"]//button[contains(text(),"Done")]')))


@then(u'Done and Skip button should be disabled')
def step_impl(context):
    driver = context.browser # type: selenium.webdriver.Firefox
    current_todo_id = context.current_todo_id
    done_button = driver.find_element(By.XPATH, '//li[@data-region-id="'+str(current_todo_id)+'_region"]//button[contains(text(),"Done")]')
    skip_button = driver.find_element(By.XPATH, '//li[@data-region-id="'+str(current_todo_id)+'_region"]//button[contains(text(),"Skip")]')
    assert_that("ui-state-disabled" in done_button.get_attribute("class")).is_true()
    assert_that("ui-state-disabled" in skip_button.get_attribute("class")).is_true()


@then(u'log of "{buttonName}" should be created and the count of should be "{new_count}"')
def step_impl(context, buttonName, new_count):
    context.browser.find_element(By.ID, "refreshData").click();
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")))
    current_todo_id = context.current_todo_id
    done_button = context.browser.find_element(By.XPATH, '//li[@data-region-id="'+str(current_todo_id)+'_region"]//button[contains(text(),"'+buttonName+' ('+new_count+')")]')
    


@then(u'the progress bar should show increase in "{color}" bar to "{percent}"')
def step_impl(context, color, percent):
    current_todo_id = context.current_todo_id
    driver = context.browser # type: selenium.webdriver.Firefox
    if color == "green":
        progressBarType = "success"
    else:
        progressBarType = "failure"
    progressBar =  driver.find_element(By.XPATH, '//li[@data-region-id="'+str(current_todo_id)+'_region"]//div[@class="progressBar-'+progressBarType+'"]')
    assert_that(progressBar.get_attribute("style")).is_equal_to("width: "+percent+";")



@when(u'user clicks on filter')
def step_impl(context):
    driver = context.browser # type: selenium.webdriver.Firefox
    driver.find_element(By.ID, "filterData").click()
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#filterPopup")))


@when(u'user selects "{filterValue}"')
def step_impl(context, filterValue):
    #Only one option is available as of now, ignoring paramaters
    driver = context.browser # type: selenium.webdriver.Firefox
    driver.find_element(By.CSS_SELECTOR, "#filterPopup label").click()
    driver.find_element(By.ID, "filterDoneButton").click()
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")))
    filter_icon = driver.find_element(By.ID, "filterData")
    assert_that("filter-active" in filter_icon.get_attribute("class")).is_true()

@then(u'"{taskName}" should be visible')
def step_impl(context, taskName):
    tasks_region = context.browser.find_elements(By.CSS_SELECTOR,"li[data-region-id]")
    for task_region in tasks_region:
        taskNameFromBrowser = task_region.find_elements(By.CSS_SELECTOR,".ui-li-header")[0].text
        if taskName == taskNameFromBrowser:
            assert_that(True).is_true()
            return
    assert_that(False).is_true()
    
@then(u'"{taskName}" should be hidden')
def step_impl(context, taskName):
    tasks_region = context.browser.find_elements(By.CSS_SELECTOR,"li[data-region-id]")
    for task_region in tasks_region:
        taskNameFromBrowser = task_region.find_elements(By.CSS_SELECTOR,".ui-li-header")[0].text
        if taskName == taskNameFromBrowser:
            assert_that(False).is_true()
            return
    assert_that(True).is_true()


@when(u'user clears the filters')
def step_impl(context):
    driver = context.browser # type: selenium.webdriver.Firefox
    driver.find_element(By.ID, "filterClearButton").click()
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")))
    filter_icon = driver.find_element(By.ID, "filterData")
    assert_that("filter-active" in filter_icon.get_attribute("class")).is_false()
