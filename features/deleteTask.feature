Feature: Delete Task

  Scenario: Delete an existing task
    Given the user is on task list page
    When user already has a non-habit task "HabitDelete" with frequency "Daily" and due date as "01-Apr-2018"
    And user clicks on the task "HabitDelete" to edit it
    And user clicks on delete button
    And user confirms delete
    Then "HabitDelete" task should not exists on home
