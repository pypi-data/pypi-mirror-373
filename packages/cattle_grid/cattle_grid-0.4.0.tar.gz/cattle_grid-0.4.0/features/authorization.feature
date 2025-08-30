Feature: Authorization for Fediverse objects.
    Something completely missing from ActivityPub.

    Background:
        Given A new user called "Alice"
        And A new user called "Bob"
        And A new user called "Claire"

    Scenario Outline: No relationship
        When "Alice" creates an object addressed to "<recipients>"
        Then "Bob" is "<state>" to view this object
        Examples:
            | recipients | state        |
            | Bob        | authorized   |
            | Claire     | unauthorized |
            | followers  | unauthorized |
            | public     | authorized   |

    Scenario Outline: Blocked
        Given  "Alice" blocks "Bob"
        When "Alice" creates an object addressed to "<recipients>"
        Then "Bob" is "<state>" to view this object
        Examples:
            | recipients | state        |
            | Bob        | unauthorized |
            | Claire     | unauthorized |
            | followers  | unauthorized |
            | public     | unauthorized |

    Scenario Outline: Following
        Given "Bob" follows "Alice"
        When "Alice" creates an object addressed to "<recipients>"
        Then "Bob" is "<state>" to view this object
        Examples:
            | recipients | state        |
            | Bob        | authorized   |
            | Claire     | unauthorized |
            | followers  | authorized   |
            | public     | authorized   |
