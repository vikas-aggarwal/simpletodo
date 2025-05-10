from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from behave import then, given, when
from assertpy import assert_that
import time

@when(u'user clicks on Create Category')
def step_impl(context):
    new_category_link = context.browser.find_element(By.ID, "new_category")
    new_category_link.click()


@when(u'user enters "{category}" as category display name')
def step_impl(context, category):
    display_name = context.browser.find_element(By.ID, "category_display_name")
    display_name.send_keys(category)


@when(u'user enters "{category}" as category internal name')
def step_impl(context, category):
    internal_name = context.browser.find_element(By.ID, "category_internal_name")
    internal_name.send_keys(category)


@when(u'user enters "{color}" as category background color')
def step_impl(context, color):
    color_field = context.browser.find_element(By.ID, "category_background")
    context.browser.execute_script( 'arguments[0].value = arguments[1]',color_field, color)



@then(u'a new category should be created with "{category}" as text, "{internal_val}" as internal value and "{color}" as background')
def step_impl(context, category, color, internal_val):
    context.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for=create_cat_"+internal_val+"]")))
    category = context.browser.find_element(By.CSS_SELECTOR, "label[for=create_cat_"+internal_val+"]")
    category.click()
    computed_color = context.browser.execute_script('return window.getComputedStyle(document.querySelector("label[for=create_cat_'+ internal_val +']")).getPropertyValue("background-color")')
    assert_that(color).is_equal_to(computed_color)
