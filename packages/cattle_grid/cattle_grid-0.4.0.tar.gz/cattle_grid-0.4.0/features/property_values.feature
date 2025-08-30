Feature: Managing Property Values
    Background:
        Given A new user called "Alice" on "abel"

    Scenario: Add a new property value
        When "Alice" adds the PropertyValue "secure" with value "yes"
        And "Alice" retrieves the object with the actor id of "Alice"
        Then The profile contains the property value "secure" with value "yes"

    Scenario: Updates a new property value
        Given "Alice" has the PropertyValue "secure" with value "yes"
        When "Alice" updates the PropertyValue "secure" with value "no"
        And "Alice" retrieves the object with the actor id of "Alice"
        Then The profile contains the property value "secure" with value "no"

    Scenario: Removes a new property value
        Given "Alice" has the PropertyValue "secure" with value "yes"
        When "Alice" removes the PropertyValue "secure"
        And "Alice" retrieves the object with the actor id of "Alice"
        Then The profile does not contain the property value "secure"