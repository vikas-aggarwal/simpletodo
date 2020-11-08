import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from behave import then, given, when
from assertpy import assert_that
import selenium

@then(u'the user is on task list page')
def user_is_on_tasklist_page(context):
    pass

    
@given(u'the user is on task list page')
def userOnTaskListPage(context):
    context.browser.get(context.protocol+"://"+context.host+":"+context.port+"/todos/home")
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form[name='taskForm']")))


@when(u'user clicks on New')
def userClicksOnNew(context):
    new_button_link = context.browser.find_element_by_id("new_task")
    new_button_link.click()

@when(u'clicks on submit')
def userClicksOnSubmit(context):
    createSubmitBtn = context.browser.find_element(By.CSS_SELECTOR, "input[type='submit']"); 
    createSubmitBtn.click()


@then(u'a new task should be created')
def newTaskStep(context,expectedTasksCount="1"):
    driver = context.browser # type: selenium.webdriver.Firefox
    task_count = len(driver.find_elements_by_class_name("task"))
    context.foundNewTask = []
    assert_that(task_count).is_equal_to(int(expectedTasksCount))
    for task in driver.find_elements_by_class_name("task"):
        context.foundNewTask.append(task)


@then(u'Task title is "{title}"')
def task_title_is(context, title, index=0):
    assert_that(context.foundNewTask[index].find_element_by_class_name("taskTitle").text).is_equal_to(title)


@when(u'user enters "{title}" on title field')
def user_enters_title(context,title):
    taskTitle = context.browser.find_element_by_id("create_taskTitle")
    taskTitle.send_keys(title)

@then(u'Task Due Date is "{dueDate}"')
def task_due_date_is(context, dueDate):
    if dueDate == "today":
        dueDateString = datetime.datetime.now().strftime(context.dateFormatForFeature);
    else:
        dueDateString = dueDate;
    due_date_str = context.foundNewTask[0].find_element_by_class_name("dueDateStr").text
    due_date_to_verify = datetime.datetime.strptime(due_date_str, context.dateFormatFromInputText).strftime(context.dateFormatForFeature)
    assert_that(due_date_to_verify).is_equal_to(dueDateString);


@when(u'user enters "{freq}" on the frequency field')
def user_enters_frequency(context,freq):
    frequency = context.browser.find_element_by_id("create_freq");
    frequency.send_keys(freq);


@then(u'Task Frequency is "{freq}"')
def task_frequency_is(context,freq):
    frequencyText = context.foundNewTask[0].find_element_by_class_name("frequencyStr").text
    assert_that(frequencyText).is_equal_to(freq);
    


@then(u'Task Next is "{noOfDays}" day after "{dueDate}"')
def task_next_is(context,noOfDays,dueDate):
    if dueDate == "today":
        dueDateString = datetime.datetime.now().strftime(context.dateFormatForFeature);
    else:
        dueDateString = dueDate;
        
    nextDate = datetime.datetime.strptime(dueDateString, context.dateFormatForFeature) + datetime.timedelta(days=int(noOfDays))
    nextDateString = nextDate.strftime(context.dateFormatForFeature)
    nextDateSpan = context.foundNewTask[0].find_element_by_css_selector(".nextDate input")
    next_date_to_verify = datetime.datetime.strptime(nextDateSpan.get_attribute("value"), context.dateFormatForInput).strftime(context.dateFormatForFeature)
    assert_that(next_date_to_verify).is_equal_to(nextDateString);


@when(u'user enters due date as "{dueDate}"')
def enter_task_due_date(context, dueDate):
    dueDateElement = context.browser.find_element_by_id("create_dueDate")
    dueDateElement.send_keys(datetime.datetime.strptime(dueDate, context.dateFormatForFeature).strftime(context.dateFormatForInput))


@when(u'user selects slot "{slotNumber}"')
def user_selects_slot(context, slotNumber):
    slot = context.browser.find_element_by_css_selector("label[for=create_slot"+slotNumber+"]")
    slot.click()


@then(u'"{noOfTasks}" new tasks should be created')
def new_tasks_to_be_created(context, noOfTasks):
    newTaskStep(context, noOfTasks)

@then(u'"{beforeTask}" should appear before "{afterTask}" in today')
def appear_before(context, beforeTask, afterTask):
    task_title_is(context, beforeTask, 0)
    task_title_is(context, afterTask, 1)

@when(u'user enters "{noOfDays}" in remind before field')
def step_impl(context,noOfDays):
    remindBefore = context.browser.find_element_by_id("create_remindBeforeDays")
    remindBefore.send_keys(noOfDays)

@then(u'"{taskName}" should appear in the alerts section')
def task_appear_in_alerts(context,taskName):
    taskListWebElement = context.browser.find_elements_by_class_name("taskList")[0]
    taskListElements = taskListWebElement.find_elements_by_class_name("task")
    foundInAlert = len(taskListElements) == 1
    assert_that(foundInAlert).is_true();    

    

@when(u'user enters due date "{noOfDays}" days in future')
def step_impl(context,noOfDays):
    dueDateString = (datetime.datetime.now() + datetime.timedelta(days=int(noOfDays))).strftime(context.dateFormatForFeature)
    enter_task_due_date(context, dueDateString)


@when(u'user selects Track Habit')
def user_selects_track_habit(context):
    track_habit = context.browser.find_element_by_css_selector("label[for=create_trackHabit")
    track_habit.click()


@then(u'"{taskName}" should have Done and Skip button with 0 count')
def step_impl(context,taskName):
    task = context.foundNewTask[0]
    task_title_is(context, taskName)
    buttons = task.find_elements_by_class_name("button_labels")
    assert_that(len(buttons)).is_equal_to(3)
    assert_that(buttons[0].text).is_equal_to("X")
    assert_that(buttons[1].text).is_equal_to("Done (0)")
    assert_that(buttons[2].text).is_equal_to("Skip (0)")
    
    
