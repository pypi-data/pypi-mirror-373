Feature: Managing identifiers

    Background:
        Given A new user called "Alice" on "abel"

    Scenario: Webfinger resolve
        When One queries webfinger for "acct:Alice@abel"
        Then The actor URI of "Alice" is returned

    Scenario: Add new primary identifier; resolve works
        Given "Alice" adds "acct:alex@abel" as a primary identifier
        When One queries webfinger for "acct:alex@abel"
        Then The actor URI of "Alice" is returned

    Scenario: Add new primary identifier; actor objet
        Given "Alice" adds "acct:alex@abel" as a primary identifier
        When "Alice" retrieves the object with id "acct:alex@abel"
        Then The preferred username is "alex"
        And "acct:alex@abel" is contained in the identifiers array

    @wip
    Scenario: Add new primary identifier; unverifiable identifier
        Given "Alice" adds "acct:alex@unknown.test" as a primary identifier
        When "Alice" retrieves the object with id "acct:Alice@abel"
        Then The preferred username is "Alice"
        And "acct:alex@unknown.test" is not contained in the identifiers array