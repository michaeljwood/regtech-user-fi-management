# User and Financial Institutions Management API
This app communicates with Keycloak to provide some user management functionality, as well as serving as `Institutions API` to retrieve information about institutions.

### Dependencies
[Poetry](https://python-poetry.org/) is used as the package management tool. Once installed, just running `poetry isntall` in the root of the project should install all the dependencies needed by the app.

## Pre-requesites
Keycloak needs to be running, and configured through environment variables, or using `.env` file, refer to [.env.local](./src/.env.local) file for all the variables. Institutions Postgres DB also needs to running, and configured, refer to [.env.local](./src/.env.local).

## Routers
There are 2 major functionalities provided by this app, one serves as the integration with Keycloak, and the other to integrate with Institutions database to show institutions' information. Below are the routers for these functionalities. Note, authentication is required to access the endpoints.
- The [admin](./src/routers/admin.py) router with `/v1/admin` path manages Keycloak integration, allow for things like update user information (i.e. First Name, Last Name), and associating with institutions
  - GET `/v1/admin/me` displays the current user's info based on the auth token provided
  - PUT `/v1/admin/me` allows for basic info update:
    ```json
    {
      "firstName": "Test",
      "lastName": "User"
    }
    ```
  - PUT `/v1/admin/me/institutions` allows for self association with institutions using LEI
    ```json
    ["TEST1LEI", "TEST2LEI"]
    ```
- The [institutions](./src/routers/institutions.py) router with `/v1/institutions` path retrieves institutions information
  - GET `/v1/institutions` retrieves all institutions in the database
    - three accepted parameters allows for filtering and pagination:
      - `page`: page of the results, this is index based, so starts with `0`
      - `count`: the number of results per page, by default this is `100`
      - `domain`: the filter parameter to look for institutions with specified domain
  - POST `/v1/institutions` creates or updates an institution with its LEI as the key:
    ```json
    {
      "lei": "TESTBANK123",
      "name": "Test Bank 123"
    }
    ```
  - POST `/v1/institutions/{LEI}/domains` adds domains to the institution:
    ```json
    [
      {
        "domain": "test123.bank"
      },
      {
        "domain": "bank123.test"
      }
    ]
    ```
For both these routers, the needed roles to access each endpoint is decorated with the `@requires` decorator, i.e. `@requires(["query-groups", "manage-users"])`; these roles corresponds to Keycloak's roles.