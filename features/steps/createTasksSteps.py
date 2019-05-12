import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from behave import *
from assertpy import *




@then(u'the user is on task list page')
def user_is_on_tasklist_page(context):
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")))
    main_page_elem = context.browser.find_element_by_id("mainpage")
    assert main_page_elem.get_attribute("class").index("ui-page-active") != -1




@given(u'the user is on task list page')
def step_impl(context):
    context.browser.get(context.protocol+"://"+context.host+":"+context.port+"/static/index.html")
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")))
    main_page_elem = context.browser.find_element_by_id("mainpage")
    assert main_page_elem.get_attribute("class").index("ui-page-active") != -1


@when(u'user clicks on New')
def step_impl(context):
    new_button_link = context.browser.find_element_by_xpath("/html/body/div[2]/div[1]/a")
    new_button_link.click()
    context.wait.until(EC.element_to_be_clickable((By.ID, "createSubmitBtn")))


@when(u'clicks on submit')
def step_impl(context):
    createSubmitBtn = context.browser.find_element_by_id("createSubmitBtn")
    createSubmitBtn.click()


@then(u'a new task should be created')
def newTaskStep(context,expectedTasksCount="1"):
    #first get all tasks in today
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")))
    oldTasks = context.browser.find_elements(By.CSS_SELECTOR,"a[id$='_edit_link']")
    oldTaskIDs = []
    for task in oldTasks:
        oldTaskIDs.append(task.get_attribute("id"))

    #refresh the page
    context.browser.refresh()
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")))
    
    #get the new task and verify
    currentTasks = context.browser.find_elements(By.CSS_SELECTOR,"a[id$='_edit_link']")

    foundTasksCount = 0
    foundNewTask = []
    for task in currentTasks:
        if task.get_attribute("id") not in oldTaskIDs:
            foundNewTask.append(task)
            foundTasksCount = foundTasksCount+1
    context.foundNewTask = foundNewTask
    assert_that(foundTasksCount).is_equal_to(int(expectedTasksCount))


            
@then(u'Task title is "{title}"')
def step_impl(context,title):
    assert_that(context.foundNewTask[0].text).is_equal_to(title)


@when(u'user enters "{title}" on title field')
def step_impl(context,title):
    taskTitle = context.browser.find_element_by_id("create_taskTitle")
    taskTitle.send_keys(title)

@then(u'Task Due Date is "{dueDate}"')
def step_impl(context, dueDate):
    if dueDate == "today":
        dueDateString = datetime.datetime.now().strftime(context.dateFormatForFeature);
    else:
        dueDateString = dueDate;
    taskId = context.foundNewTask[0].get_attribute("id");
    dueDateSpan = context.browser.find_element_by_id(taskId[0:taskId.index('_')]+"_label_due").text
    due_date_to_verify = datetime.datetime.strptime(dueDateSpan, context.dateFormatFromInputText).strftime(context.dateFormatForFeature)
    assert_that(due_date_to_verify).is_equal_to(dueDateString);


@when(u'user enters "{freq}" on the frequency field')
def step_impl(context,freq):
    frequency = context.browser.find_element_by_id("create_freq");
    frequency.send_keys(freq);


@then(u'Task Frequency is "{freq}"')
def step_impl(context,freq):
    taskId = context.foundNewTask[0].get_attribute("id");
    frequencyLabel = context.browser.find_element_by_id(taskId[0:taskId.index('_')]+"_frequency_label");
    assert_that(frequencyLabel.text).is_equal_to(freq);
    


@then(u'Task Next is "{noOfDays}" day after "{dueDate}"')
def step_impl(context,noOfDays,dueDate):
    if dueDate == "today":
        dueDateString = datetime.datetime.now().strftime(context.dateFormatForFeature);
    else:
        dueDateString = dueDate;
        
    nextDate = datetime.datetime.strptime(dueDateString, context.dateFormatForFeature) + datetime.timedelta(days=int(noOfDays))
    nextDateString = nextDate.strftime(context.dateFormatForFeature)
    taskId = context.foundNewTask[0].get_attribute("id")
    nextDateSpan = context.browser.find_element_by_id(taskId[0:taskId.index('_')]+"_date")
    next_date_to_verify = datetime.datetime.strptime(nextDateSpan.get_attribute("value"), context.dateFormatForInput).strftime(context.dateFormatForFeature)
    assert_that(next_date_to_verify).is_equal_to(nextDateString);


@when(u'user enters due date as "{dueDate}"')
def enter_task_due_date(context, dueDate):
    dueDateElement = context.browser.find_element_by_id("create_dueDate")
    dueDateElement.send_keys(datetime.datetime.strptime(dueDate, context.dateFormatForFeature).strftime(context.dateFormatForInput))


@when(u'user selects slot "{slotNumber}"')
def step_impl(context, slotNumber):
    slot = context.browser.find_element_by_css_selector("label[for=create_slot"+slotNumber+"]")
    slot.click()


@then(u'"{noOfTasks}" new tasks should be created')
def step_impl(context, noOfTasks):
    newTaskStep(context, noOfTasks)

@then(u'"{beforeTask}" should appear before "{afterTask}" in today')
def step_impl(context, beforeTask, afterTask):
    #TODO check for today
    assert_that(context.foundNewTask[0].text).is_equal_to(beforeTask)
    assert_that(context.foundNewTask[1].text).is_equal_to(afterTask)

@when(u'user enters "{noOfDays}" in remind before field')
def step_impl(context,noOfDays):
    remindBefore = context.browser.find_element_by_id("create_remindBeforeDays")
    remindBefore.send_keys(noOfDays)

@then(u'"{taskName}" should appear in the alerts section')
def step_impl(context,taskName):
    taskListWebElement = context.browser.find_element_by_id("tasklistdata")
    taskListElements = taskListWebElement.find_elements_by_tag_name("li")
    inAlert = False;
    foundInAlert = False;
    for taskElem in taskListElements:
        if taskElem.get_attribute("data-role") == "list-divider":
            if taskElem.text == "Alerts":
                inAlert = True;
            else:
                inAlert = False;
        elif inAlert and  context.foundNewTask[0].text == taskElem.find_element_by_class_name("ui-li-header").text :
            foundInAlert = True;

    assert_that(foundInAlert).is_true();    

    

@when(u'user enters due date "{noOfDays}" days in future')
def step_impl(context,noOfDays):
    dueDateString = (datetime.datetime.now() + datetime.timedelta(days=int(noOfDays))).strftime(context.dateFormatForFeature)
    enter_task_due_date(context, dueDateString)


@when(u'user selects Track Habit')
def step_impl(context):
    track_habit = context.browser.find_element_by_xpath("/html/body/div[3]/div[2]/div[4]/label")
    track_habit.click()


@then(u'"{taskName}" should have Done and Skip button with 0 count')
def step_impl(context,taskName):
    taskEditLinkID = context.foundNewTask[0].get_attribute("id")
    taskID = taskEditLinkID[0:taskEditLinkID.index('_')]
    taskRegion = context.browser.find_elements(By.CSS_SELECTOR,"li[data-region-id='"+taskID+"_region']")[0]
    buttons = taskRegion.find_elements_by_tag_name("button")
    assert_that(len(buttons)).is_equal_to(2)
    assert_that(buttons[0].text).is_equal_to("Done (0)")
    assert_that(buttons[1].text).is_equal_to("Skip (0)")
    
    
