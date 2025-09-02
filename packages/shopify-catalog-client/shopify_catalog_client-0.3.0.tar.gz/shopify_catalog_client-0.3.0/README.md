# Shopify Client

A Python client for Shopify's GraphQL API.

## Code Generation

```sh
ariadne-codegen
```

## Testing

Use `pytest` to run tests:
```sh
pytest
```

Use `pytest-watch` to run tests continuously:
```sh
ptw
```

Use `pytest-watch` with `pytest-xdist` to run tests continuously in parallel:
```sh
ptw -- --maxfail=1 -n auto
```

## CI

CI will run the code generation and tests against the test Shopify store configured in repo secrets.

## Publishing

```sh
hatch build --clean
hatch publish
```
