from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from behave import *;
import time;
from unittest import TestCase
from assertpy import *;
import datetime;



@then(u'the user is on task list page')
def step_impl(context):
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")));
    mainPageElem  = context.browser.find_element_by_id("mainpage");
    assert mainPageElem.get_attribute("class").index("ui-page-active")!=-1;




@given(u'the user is on task list page')
def step_impl(context):
    context.browser.get("http://localhost:5000/static/index.html");
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")));
    mainPageElem  = context.browser.find_element_by_id("mainpage");
    assert mainPageElem.get_attribute("class").index("ui-page-active")!=-1;


@when(u'user clicks on New')
def step_impl(context):
    newButtonLink = context.browser.find_element_by_xpath("/html/body/div[1]/div[1]/a");
    newButtonLink.click();
    context.wait.until(EC.element_to_be_clickable((By.ID, "createSubmitBtn")));


@when(u'clicks on submit')
def step_impl(context):
    createSubmitBtn = context.browser.find_element_by_id("createSubmitBtn");
    createSubmitBtn.click();


@then(u'a new task should be created')
def step_impl(context):
    #first get all tasks in today
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")));
    oldTasks = context.browser.find_elements(By.CSS_SELECTOR,"a[id$='_edit_link']");
    oldTaskIDs = [];
    for task in oldTasks:
        oldTaskIDs.append(task.get_attribute("id"));

    #refresh the page
    context.browser.refresh();
    context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-li-divider")));
    
    #get the new task and verify
    currentTasks = context.browser.find_elements(By.CSS_SELECTOR,"a[id$='_edit_link']");

    foundNewTask = None;
    for task in currentTasks:
        if task.get_attribute("id") not in oldTaskIDs:
            foundNewTask = task;
            context.foundNewTask = task;
    assert_that(foundNewTask).is_not_none();


            
@then(u'Task title is "{title}"')
def step_impl(context,title):
    assert_that(context.foundNewTask.text).is_equal_to(title);


@when(u'user enters "{title}" on title field')
def step_impl(context,title):
    taskTitle = context.browser.find_element_by_id("create_taskTitle");
    taskTitle.send_keys(title);

@then(u'Task Due Date is "{dueDate}"')
def step_impl(context,dueDate):
    if dueDate == "today":
        dueDateString = datetime.datetime.now().strftime("%d-%b-%Y");
    else:
        dueDateString = dueDate;
    taskId = context.foundNewTask.get_attribute("id");
    dueDateSpan = context.browser.find_element_by_id(taskId[0:taskId.index('_')]+"_label_due");
    assert_that(dueDateSpan.text).is_equal_to(dueDateString);


@when(u'user enters "{freq}" on the frequency field')
def step_impl(context,freq):
    frequency = context.browser.find_element_by_id("create_freq");
    frequency.send_keys(freq);


@then(u'Task Frequency is "{freq}"')
def step_impl(context,freq):
    taskId = context.foundNewTask.get_attribute("id");
    frequencyLabel = context.browser.find_element_by_id(taskId[0:taskId.index('_')]+"_frequency_label");
    assert_that(frequencyLabel.text).is_equal_to(freq);
    


@then(u'Task Next is "{noOfDays}" day after "{dueDate}"')
def step_impl(context,noOfDays,dueDate):
    if dueDate == "today":
        dueDateString = datetime.datetime.now().strftime("%d-%b-%Y");
    else:
        dueDateString = dueDate;
        
    nextDate = datetime.datetime.strptime(dueDateString,"%d-%b-%Y") + datetime.timedelta(days=int(noOfDays));
    nextDateString = nextDate.strftime("%d-%b-%Y");
    taskId = context.foundNewTask.get_attribute("id");
    nextDateSpan = context.browser.find_element_by_id(taskId[0:taskId.index('_')]+"_label_next");
    
    assert_that(nextDateSpan.text).is_equal_to(nextDateString);


@when(u'user enters due date as "{dueDate}"')
def step_impl(context,dueDate):
    dueDateElement = context.browser.find_element_by_id("create_dueDate");
    dueDateElement.send_keys(dueDate);

