Feature: Basic functionality
    This feature describes the basic functionality a Fediverse
    server should have. One could summarize it with: If two
    people know of each other, they could communicate.

    Background:
        Given A new user called "Alice" on "abel"

    Scenario: Webfinger resolve
        When One queries webfinger for "acct:Alice@abel"
        Then The actor URI of "Alice" is returned

    Scenario: Fetch actor
        Given A new user called "Bob"
        When "Alice" retrieves the object with the actor id of "Bob"
        Then The retrieved object is the profile of "Bob"

    @wip
    Scenario: Fetch actor
        Given A new user called "Bob" on "banach"
        When "Alice" retrieves the object with id "acct:Bob@banach"
        Then The retrieved object is the profile of "Bob"

    Scenario: Send message
        Given A new user called "bob"
        When "Alice" sends "bob" a message saying "You stole my milk!"
        Then "bob" receives a message saying "You stole my milk!"
        And "bob" can lookup this message by id

    # The last step requires a working cache

    Scenario: Delete actor
        When "Alice" deletes herself
        And One queries webfinger for "acct:Alice@abel"
        Then No actor URI is returned

    Scenario: Delete actor returns 410 gone
        Given A new user called "bob"
        When "Alice" deletes herself
        And "bob" looks up the actor id of "Alice"
        Then 410 gone is returned