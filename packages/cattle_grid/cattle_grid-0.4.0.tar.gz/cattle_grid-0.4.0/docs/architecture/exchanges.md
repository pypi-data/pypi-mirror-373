# RabbitMQ Exchanges

cattle_grid uses topic exchanges. This means that every
message has an attached routing key. These have the form
of being separated by a dot `.`, e.g.

```plain
incoming.Follow
```

## Types of Exchange

There are three exchanges used by cattle_grid:

- The __RawExchange__: Handles incoming and outgoing messages as they are transferred to the Fediverse.
- The __ActivityExchange__: You can subscribe to this exchange. Topics are organized by the type of activity, e.g. `incoming.Follow` and `outgoing.Accept`. Furthermore, this exchange is meant to contain the methods, e.g. `send_message` and `update_actor`.
- The __AccountExchange__: This exchange contains the account name as part of the routing key, e.g. `receive.Alice.incoming`.

## Message Flow

In the following, we will denote an exchange using a rounded box
with the exchange name followed by the routing key in italics, e.g.

```mermaid
flowchart LR
E(["`Exchange
_routing.key_`"])
S[Something]
E --> S
```

Square boxes are used to denote other objects. Arrows indicate the
message flow.

### Incoming messages

We now illustrate what happens when a message is send from an external
Fediverse application to cattle_grid.

```mermaid
flowchart LR
R(["`RawExchange
_incoming.*_`"])
A(["`ActivityExchange
_incoming.*_`"])
A2(["`AccountExchange
_receive.Alice.incoming_`"])

    F[Fediverse] --> |"`ActivityPub
POST /inbox`"| R
    R -->|transformer| A
    R -->|transformer| A2
    A ==> YE[Your Extensions]
    A2 ==> YC[Your Client Applications]
```

The processing of cattle_grid as described in
[ActivityPub Processing](./activitypub.md) takes place on the RawExchange.

See [cattle_grid.extensions.load.build_transformer][] for how the transformer is being constructed from extensions,
and [cattle_grid.dependencies.Transformer][] for how to inject it.

### Outgoing messages

```mermaid
flowchart LR
A(["`ActivityExchange
_send_message_`"])
R(["`RawExchange
_outgoing.*_`"])
A2(["`ActivityExchange
_outgoing.*_`"])
AP[Your application]

    AP -->|out_transformer| A
    A --> A2
    A --> R
    R --> F[Fediverse]
    A2 --> YE[Your Extension]
```

The processing of cattle_grid as described in
[ActivityPub Processing](./activitypub.md) takes place on the RawExchange.

### Fetching objects

```mermaid
flowchart LR
AP[Your application]
A(["Activity Exchange"])
R(["RawExchange"])

    AP --> A
    A --> AP
    A --> R
    R -->|transformer| A
    R -->|GET /resource| F[Fediverse]
```

!!!todo
    Check if it is really teh position of the transformer, we want.

### Serving Content

One should use the out_transformer result.
Alternatively, one can store the result of the `outgoing.*`
topic.

## Configuration

The names used for the exchange can be configured via

```toml title="cattle_grid.toml"
activity_pub.internal_exchange = "cattle_grid_internal" # RawExchange
activity_pub.exchange = "cattle_grid" # ActivityExchange
activity_pub.account_exchange = "amq.topic" # AccountExchange
```

where the prescribed values are the default values.

!!! todo
    Harmonize names
