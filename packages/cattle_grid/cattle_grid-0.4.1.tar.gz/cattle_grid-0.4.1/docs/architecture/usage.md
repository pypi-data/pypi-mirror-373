# Usage

## Activity Exchange

In vanilla cattle_grid, there are two routing_keys on
the Activity Exchange, you should send messages to:

- `send_message` ... performs POST inbox in the Fediverse
- `fetch_object` ... returns GET object in the Fediverse
