# The Cattle Drive API

This document is a link list to the synchronous and asynchronous APIs provided by cattle_grid.

!!! todo
    This is still todo

## Account API

The account API can be used to create an account. To
sign in using an account, and manage the account and
actors using this.

<div class="grid cards" markdown>

- [:material-api:{ .lg .middle } __redoc API Viewer__](./assets/redoc.html?url=openapi_account.json)

- [:material-download:{ .lg .middle } __Download OpenAPI.json__](./assets/schemas/openapi_account.json)

- [:material-code-braces:{ .lg .middle } __TypeScript SDK__](https://bovine.codeberg.page/cattle_grid/@jsdocs/)

</div>

Most methods provided by this API are synchronous. This
means that once the create account call is finished, the
account is created. Similarly, for the lookup method for
Fediverse resources: It returns the result.

The only exception is the _perform_ method that delegates
to asynchronous methods. One should note that this method
is the one used for most interactions with the Fediverse.

The other except is the stream method that creates
an EventSource.
