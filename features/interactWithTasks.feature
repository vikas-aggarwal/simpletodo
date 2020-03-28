Feature: Interact with Tasks

  Scenario: Mark a non-habit task with supported frequency as done
    Given the user is on task list page
    When user already has a non-habit task "NonHabitDone" with frequency "Daily" and due date as "01-Apr-2018"
    And user marks the task "NonHabitDone" as "Done"
    Then the due date of the task "NonHabitDone" should change to "02-Apr-2018"
    And Done button should be disabled

  Scenario: Mark a non-habit task with frequency not supported as done
    Given the user is on task list page
    When user already has a non-habit task "NonHabitDone" with frequency "Irregular" and due date as "01-Apr-2018"
    And user selects a next due date as "05-Apr-2018" as the done button is disabled
    And user marks the task "NonHabitDone" as "Done"
    Then the due date of the task "NonHabitDone" should change to "05-Apr-2018"
    And Done button should be disabled

  Scenario: Mark a habit task with supported frequency as done
    Given the user is on task list page
    When user already has a habit task "HabitDone" with frequency "Daily" and due date as "01-Apr-2018" with count "10"
    And user marks the task "HabitDone" as "Done"
    Then the due date of the task "HabitDone" should change to "22-Apr-2018"
    And Done and Skip button should be disabled
    And log of "Done" should be created and the count of should be "11"
    And the progress bar should show increase in "green" bar to "52%"

  Scenario: Mark a habit task with supported frequency as skip
    Given the user is on task list page
    When user already has a habit task "HabitSkip" with frequency "Daily" and due date as "01-Apr-2018" with count "10"
    And user marks the task "HabitSkip" as "Skip"
    Then the due date of the task "HabitSkip" should change to "22-Apr-2018"
    And Done and Skip button should be disabled
    And log of "Skip" should be created and the count of should be "11"
    And the progress bar should show increase in "red" bar to "52%"


  Scenario: Mark a habit task with frequency not supported as done
    Given the user is on task list page
    When user already has a habit task "HabitDone" with frequency "Irregular" and due date as "01-Apr-2018" with count "10"
    And user selects a next due date as "05-Apr-2018" as the done button is disabled
    And user marks the task "HabitDone" as "Done"
    Then the due date of the task "HabitDone" should change to "05-Apr-2018"
    And Done and Skip button should be disabled
    And log of "Done" should be created and the count of should be "11"
    And the progress bar should show increase in "green" bar to "52%"

  Scenario: Mark a habit task with frequency not supported as skip
    Given the user is on task list page
    When user already has a habit task "HabitSkip" with frequency "Irregular" and due date as "01-Apr-2018" with count "10"
    And user selects a next due date as "05-Apr-2018" as the done button is disabled
    And user marks the task "HabitSkip" as "Skip"
    Then the due date of the task "HabitSkip" should change to "05-Apr-2018"
    And Done and Skip button should be disabled
    And log of "Skip" should be created and the count of should be "11"
    And the progress bar should show increase in "red" bar to "52%"
    
  Scenario: Mark a new habit task with frequency not supported as done
    Given the user is on task list page
    When user already has a habit task "HabitNewDone" with frequency "Irregular" and due date as "01-Apr-2018" with count "0"
    And user selects a next due date as "05-Apr-2018" as the done button is disabled
    And user marks the task "HabitNewDone" as "Done"
    Then the due date of the task "HabitNewDone" should change to "05-Apr-2018"
    And Done and Skip button should be disabled
    And log of "Done" should be created and the count of should be "1"
    And the progress bar should show increase in "green" bar to "100%"

  Scenario: Mark a new habit task with frequency not supported as skip
    Given the user is on task list page
    When user already has a habit task "HabitNewSkip" with frequency "Irregular" and due date as "01-Apr-2018" with count "0"
    And user selects a next due date as "05-Apr-2018" as the done button is disabled
    And user marks the task "HabitNewSkip" as "Skip"
    Then the due date of the task "HabitNewSkip" should change to "05-Apr-2018"
    And Done and Skip button should be disabled
    And log of "Skip" should be created and the count of should be "1"
    And the progress bar should show increase in "red" bar to "100%"

  Scenario: Filter Daily tasks
    Given the user is on task list page
    When user already has a non-habit task "NonHabitDailyTask" with frequency "Daily" and due date as "01-Apr-2018"
    And user already has a habit task "HabitIrregular" with frequency "Irregular" and due date as "01-Apr-2018" with count "0"
    And user clicks on filter
    And user selects "Daily"
    Then "NonHabitDailyTask" should be visible
    And "HabitIrregular" should be hidden

  Scenario: Removing filter shows all tasks
    Given the user is on task list page
    When user already has a non-habit task "NonHabitDailyTask" with frequency "Daily" and due date as "01-Apr-2018"
    And user already has a habit task "HabitIrregular" with frequency "Irregular" and due date as "01-Apr-2018" with count "0"
    And user clicks on filter
    And user selects "Daily"
    And user clicks on filter
    And user clears the filters
    Then "NonHabitDailyTask" should be visible
    And "HabitIrregular" should be visible

  Scenario: Edit a Task with Irregular frequency
    Given the user is on task list page
    When user already has a non-habit task "EditIrregular" with frequency "Irregular" and due date as "01-Apr-2018"
    And user clicks on the task "EditIrregular" to edit it
    And user edits due date as "05-Nov-2018"
    And clicks on submit to edit
    Then the due date of the task "EditIrregular" should change to "05-Nov-2018"

  Scenario: User edits all the fields of a task
    Given the user is on task list page
    When user already has a non-habit task "EditIrregular" with frequency "Irregular" and due date as "01-Apr-2018"
    And user clicks on the task "EditIrregular" to edit it
    And user edits task name as "EditIrregular-1"
    And user edits frequency as "Monthly"
    And user edits due date as "05-Nov-2018"
    And user edits slot to "2"
    And user edits remind before to "5"
    And user edits Track Habit
    And clicks on submit to edit
    Then validate task with name "EditIrregular-1", frequency "Monthly", due date "05-Nov-2018", time slot "2", remind before "5" and track habit as "True"
    

  Scenario: User edits all the fields of a habit task marking Track habit as False
    Given the user is on task list page
    When user already has a habit task "EditIrregular" with frequency "Irregular" and due date as "01-Apr-2018" with count "0"
    And user clicks on the task "EditIrregular" to edit it
    And user edits task name as "EditIrregular-1"
    And user edits frequency as "Monthly"
    And user edits due date as "05-Nov-2018"
    And user edits slot to "4"
    And user edits remind before to "5"
    And user edits Track Habit
    And clicks on submit to edit
    Then validate task with name "EditIrregular-1", frequency "Monthly", due date "05-Nov-2018", time slot "4", remind before "5" and track habit as "False"

