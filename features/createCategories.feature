Feature: Create Category

  Scenario: Create a new Category and use to create a new task
    Given the user is on task list page
    When user clicks on Create Category
    And user enters "Testing" as category display name
    And user enters "testing" as category internal name
    And user enters "#f66151" as category background color
    And clicks on submit
    And user clicks on New
    Then a new category should be created with "Testing" as text, "testing" as internal value and "rgb(246, 97, 81)" as background