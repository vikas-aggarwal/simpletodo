import json
import http
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from behave import then, when
from assertpy import assert_that
import selenium

def submit_form(context):
    context.browser.find_element(By.CSS_SELECTOR, ".form_submit_button input").click()


def create_task(payload, host, port):
    http_client = http.client.HTTPConnection(host, port)
    http_client.request("POST", "/todos", json.dumps(payload), {'Content-Type': 'application/json'})
    response = http_client.getresponse()
    assert_that(response.status).is_equal_to(200)
    return json.load(response)['todo_id']

def create_task_log(payload, todo_id, host, port):
    http_client = http.client.HTTPConnection(host, port)
    http_client.request("POST", "/todos/action/"+str(todo_id), json.dumps(payload), {'Content-Type': 'application/json'})
    response = http_client.getresponse()
    assert_that(response.status).is_equal_to(200)

def get_task(todo_id, host, port):
    http_client = http.client.HTTPConnection(host, port)
    http_client.request("GET", "/todos/"+str(todo_id))
    response = http_client.getresponse()
    assert_that(response.status).is_equal_to(200)
    return json.load(response)


@when(u'user already has a non-habit task "{taskName}" with frequency "{frequency}" and due date as "{dueDate}"')
def create_non_habit_task(context, taskName, frequency, dueDate):
    payload = {}
    payload['frequency'] = frequency
    payload['task'] = taskName
    payload['due_date'] = datetime.datetime.strptime(dueDate, context.dateFormatForFeature).timestamp()
    todo_id = create_task(payload, context.host, context.port)
    context.current_todo_id = todo_id
    driver = context.browser  # type: selenium.webdriver.Firefox
    driver.refresh()


@when(u'user already has a habit task "{taskName}" with frequency "{frequency}" and due date as "{dueDate}" with count "{count}"')
def create_habit_task(context, taskName, frequency, dueDate, count):
    payload = {}
    payload['frequency'] = frequency
    payload['task'] = taskName
    payload['trackHabit'] = True
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
    driver = context.browser  # type: selenium.webdriver.Firefox
    driver.refresh()


@when(u'user marks the task "{taskName}" as "{action}"')
def mark_task_done_or_skip(context, taskName, action):
    action_button = context.browser.find_element_by_css_selector("label[for=\""+str(context.current_todo_id)+"_"+action.lower()+"\"]")
    action_button.click()
    context.actionButton = action_button
    submit_form(context)

@then(u'the due date of the task "{taskName}" should change to "{newDueDate}"')
def due_date_of_task_should_change_to(context, taskName, newDueDate):
    due_date = context.browser.find_element_by_class_name("dueDateStr").text
    due_date_to_verify = datetime.datetime.strptime(due_date, context.dateFormatFromInputText).strftime(context.dateFormatForFeature)
    assert_that(due_date_to_verify).is_equal_to(newDueDate)

@when(u'user selects a next due date as "{newDueDate}"')
def user_selects_next_due(context, newDueDate):
    driver = context.browser  # type: selenium.webdriver.Firefox
    current_todo_id = context.current_todo_id
    newDueDateInISOFormat = datetime.datetime.strptime(newDueDate, context.dateFormatForFeature).strftime(context.dateFormatForInput)
    driver.find_element(By.CSS_SELECTOR, "input[name=\""+str(current_todo_id)+"_next_due\"]").send_keys(newDueDateInISOFormat)

@then(u'log of "{buttonName}" should be created and the count of should be "{new_count}"')
def step_impl(context, buttonName, new_count):
    current_todo_id = context.current_todo_id
    selector = 'label[for="'+str(current_todo_id)+"_"+buttonName.lower()+'"]'
    done_label = context.browser.find_element(By.CSS_SELECTOR, selector)
    assert_that(done_label.text).is_equal_to(buttonName+" ("+new_count+")")

##NOT USED, RETAINED FOR FUTURE
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
    driver.find_element(By.ID, "new_filter").click()


@when(u'user selects "{filterValue}"')
def step_impl(context, filterValue):
    #Only one option is available as of now, ignoring paramaters
    driver = context.browser # type: selenium.webdriver.Firefox
    context.browser.find_element_by_xpath('//a[text()="'+filterValue+'"]').click()
    assert_that(driver.find_element_by_id("clear_filter").is_displayed()).is_true()

@then(u'"{taskName}" should be visible')
def step_impl(context, taskName):
    tasks_region = context.browser.find_elements(By.CSS_SELECTOR, ".taskListWithHeader")
    for task_region in tasks_region:
        taskNameElement = task_region.find_elements(By.CSS_SELECTOR, ".taskTitle a")
        if len(taskNameElement) > 0:
            for taskEntry in taskNameElement:
                taskNameFromBrowser = taskEntry.text
                if taskName == taskNameFromBrowser:
                    assert_that(True).is_true()
                    return
    assert_that(False).is_true()
    
@then(u'"{taskName}" should be hidden')
def step_impl(context, taskName):
    tasks_region = context.browser.find_elements(By.CSS_SELECTOR,".taskListWithHeader")
    for task_region in tasks_region:
        taskNameElement = task_region.find_elements(By.CSS_SELECTOR, ".taskTitle a")
        if len(taskNameElement) > 0:
            for taskEntry in taskNameElement:
                taskNameFromBrowser = taskEntry.text
                if taskName == taskNameFromBrowser:
                    assert_that(False).is_true()
                    return
    assert_that(True).is_true()


@when(u'user clears the filters')
def step_impl(context):
    driver = context.browser # type: selenium.webdriver.Firefox
    driver.find_element(By.ID, "clear_filter").click()
    assert_that(driver.find_element_by_id("new_filter").is_displayed()).is_true()

@when(u'user clicks on the task "{taskName}" to edit it')
def step_impl(context, taskName):
    driver = context.browser # type: selenium.webdriver.Firefox
    tasks = context.browser.find_elements(By.CSS_SELECTOR,".taskTitle>a")
    for task in tasks:
        if task.text == taskName:
            task.click()
            return

@when(u'user edits due date as "{dueDate}"')
def enter_task_due_date(context, dueDate):
    dueDateElement = context.browser.find_element_by_id("edit_dueDate")
    dueDateElement.send_keys(datetime.datetime.strptime(dueDate, context.dateFormatForFeature).strftime(context.dateFormatForInput))


@when(u'clicks on submit to edit')
def step_impl(context):
    editSubmitBtn = context.browser.find_element_by_css_selector("input[type='submit']")
    editSubmitBtn.click()

@when(u'user edits task name as "{title}"')
def step_impl(context,title):
    taskTitle = context.browser.find_element_by_id("edit_taskTitle")
    taskTitle.clear()
    taskTitle.send_keys(title)

@when(u'user edits frequency as "{freq}"')
def step_impl(context,freq):
    browser = context.browser # type: selenium.webdriver.Firefox
    frequency = browser.find_element_by_id("edit_freq")
    frequency.clear()
    frequency.send_keys(freq)

@when(u'user edits slot to "{slotNumber}"')
def step_impl(context, slotNumber):
    slot = context.browser.find_element_by_css_selector("label[for=edit_slot"+slotNumber+"]")
    slot.click()

@when(u'user edits remind before to "{noOfDays}"')
def step_impl(context,noOfDays):
    remindBefore = context.browser.find_element_by_id("edit_remindBeforeDays")
    remindBefore.send_keys(noOfDays)

@when(u'user edits Track Habit')
def step_impl(context):
    track_habit = context.browser.find_element_by_xpath("/html/body/form/table/tbody/tr[6]/td/label")
    track_habit.click()

@then(u'validate task with name "{task_name}", frequency "{frequency}", due date "{due_date}", time slot "{timeSlot}", remind before "{remindBefore}" and track habit as "{trackHabit}"')
def step_impl(context, task_name, frequency, due_date, timeSlot, remindBefore, trackHabit):
    taskData = get_task(1, context.host, context.port)[0]
    assert_that(frequency).is_equal_to(taskData['frequency'])
    assert_that(task_name).is_equal_to(taskData['task'])
    assert_that(due_date).is_equal_to(datetime.datetime.fromtimestamp(taskData['due_date']['$date']/1000).strftime(context.dateFormatForFeature))
    assert_that(timeSlot).is_equal_to(str(taskData['timeSlot']))
    assert_that(remindBefore).is_equal_to(str(taskData['remindBeforeDays']))
    assert_that(trackHabit).is_equal_to(str(taskData['trackHabit']))
