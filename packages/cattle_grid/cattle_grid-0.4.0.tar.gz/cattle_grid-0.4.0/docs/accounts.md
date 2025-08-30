# Accounts in cattle_grid

The basic level of access control provided by
cattle_grid is base on accounts. Each account has a
__name__ and a __password__, and these are used for
authentication, e.g. when [connecting to RabbitMQ](reference_account/account.rabbitmq.md).

Once you have an account, you are able to:

- Obtain information about the backend and your actors
- Create new actors
- Perform actions as your actor, including updating, deleting, and fetching Fediverse resources.

Currently, there are few restrictions, except that the
actor must belong to the account. This is planned to change.

## Managing accounts

### Creating an account

An admin account can currently be created via the command line

```bash
python -mcattle_grid account new NAME PASSWORD --admin
```

Other permissions can be granted to the account at creation
via

```bash
python -mcattle_grid account new NAME PASSWORD --permission one --permission two
```

### Listing accounts

This can be done via the command line

```bash
python -mcattle_grid account list
```

### Modifying permissions of an account

One can add and remove permissions as follows

```bash
python -mcattle_grid account modify NAME \
    --add_permission three \
    --remove_permission two
```

## Configuration

### Defining permissions

Currently, the set of base urls, an account is allowed to create actors
under can be limited by permissions. For this create a file

```toml title="config/one.toml"
[permissions.one]

base_urls = ["https://domain.example"]
```

Here `base_urls` is a list of urls without terminating slash. `one`
will be the name of the permission. The admin permission is valid
for all configured base urls.

### Validation of the account name

Configuration for accounts is under the `account` key. Default values
and configuration names can be found in
[cattle_grid.config.validators.account_validations][].

!!! warning
    I'm unsure what would happen if one allows many special characters
    in the account name. This is due to the account name being
    used as part of a routing_key, e.g. `receive.Alice.incoming`.
    For example, allowing a dot `.` in the account name would
    break certain parts of the logic.

### Automatically adding accounts in a test bed

By adding

```toml title="config/testing.toml"
[testing]
enable = true

[[testing.accounts]]
name = "test"
password = "pass"
permissions = ["admin"]
```

one can automatically create an account with credentials
`test` and `pass` and admin permissions on application start.
This is useful, if you often delete your instance, and
want to automatically create accounts.
