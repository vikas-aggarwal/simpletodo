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
