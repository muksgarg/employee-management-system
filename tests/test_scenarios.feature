Feature: Employee Management System Enhancement Suite
  As an HR Administrator
  I want to edit, delete, and search employee records
  So that the employee database remains accurate and easily navigable.

  Background:
    Given the Employee Management System is running locally
    And the SQLite database is initialized with default schema

  # Enhancement 1: Edit Employee
  Scenario: Successfully update an existing employee details
    Given an employee exists in the database
    When the user submits updated details for the employee
    Then the database should reflect the updated details
    And a successful redirect status code should be returned

  # Enhancement 2: Delete Employee
  Scenario: Successfully delete an employee record
    Given an employee with ID 1 exists in the database
    When the user triggers the delete action for employee ID 1
    Then the record should be permanently removed from the SQLite database

  # Enhancement 3: Search and Filter Employees
  Scenario: Search employees by matching name keyword
    Given employees exist in the database
    When the user enters a search filter query
    Then the resulting list should only display matching records