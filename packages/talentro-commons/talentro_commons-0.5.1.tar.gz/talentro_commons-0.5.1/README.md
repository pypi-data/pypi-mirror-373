# Talentro definitions

This package contains all models and data structures for Talentro
It is exclusively meant for the Talentro ecosystem.

## Initial run

- Run `poetry self update && poetry self add keyrings.google-artifactregistry-auth`
- Run `poetry config repositories.gcp https://europe-west4-python.pkg.dev/talentro-459113/talentro-python`

## How to create a new version

- Make changes in the code, like editing the models
- Bump the version number to desired version in `pyproject.toml` using the `major.minor.fix` format
- run `poetry publish --build --repository gcp`

Now a new version is uploaded to pypi and you can install it after a minute in the other projects.