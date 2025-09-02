# Generated Neops GraphQL Client

```shell
pip install neops_graphql
```

**ALPHA**

A low level generated graphql client for neops.

This is an low level client and should not be included directly into a project

## Generate a new Cliebt

To generate a new client, execute following steps

```shell
make get-latest-schema
poetry install --no-root
poetry run ariadne-codegen
poetry build
```

## Publish a new client

```shell
# Get API token on pypi
poetry config pypi-token.pypi your-api-token
poetry publish
```