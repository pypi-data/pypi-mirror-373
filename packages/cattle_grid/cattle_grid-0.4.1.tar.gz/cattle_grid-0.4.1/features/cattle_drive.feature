Feature: Cattle Drive

    Background:
        Given An account called "Alice"

    Scenario:
        Given "Alice" created an actor called "Alyssa"
        When "Alice" deletes the actor "Alyssa"
        Then "Alice" has no actors