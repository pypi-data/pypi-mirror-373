# Architecture

<div class="grid cards" markdown>

- [:material-api:{ .lg .middle } __Exchange AsyncAPI__](../assets/asyncapi.html?url=asyncapi_exchange.json)

</div>

cattle_grid's architecture has a few components, we will
first define here:

- Accounts serve as the main grouping things and internal authorization mechanism.
- Fediverse / ActivityPub Actors belong to an account
- RabbitMQ exchanges are used to both process incoming messages and send outgoing messages
- Certain APIs are used to provide additional services

These things are all _internal_. The interface exposed to
the Fediverse are the ActivityPub actors. In particular,
the account has no meaning outside of cattle_grid.

## Accounts and Actors

Each account has a unique name. This name is used in
the _AccountExchange_ to provide two routing_keys:

- `send.{account_name}`
- `receive.{account_name}`

which are accessible to this account. The receive
topic contains all the activities meant for this account.
The send topic can be used to send activities to the
Fediverse.

Generally, administrative tasks should be performed
through the API.

!!! warning
    Distinguish what should be done via API and send topic

## RabbitMQ Exchanges

cattle_grid has three exchanges:

- The AccountExchange: For external applications
- The ActivityExchange: For extensions
- The internal exchange: That's for preprocessing ActivityPub stuff. You shouldn't have to interact with this one.

### The ActivityExchange

Where the AccountExchange routes messages based on who
it belongs to, as is useful for building user facing
applications, the ActivityExchange routes messages
based on the type of activity.

For example the simple storage plugin defines the
routing key `simple_storage_publish_activity`. So, to
use it you would send a message with content

```json
{
    "type": "simple_storage_publish_activity",
    "actor": "acct:alice@abel",
    "activity": {
        "type": "AnimalSound",
        "attributedTo": "acct:alice@abel",
        "content": "moooo",
        "to": "acct:bob@banach",
    }
}
```

The processing of the AccountExchange would then route
this message to the ActivityExchange with the
correct routing key.
