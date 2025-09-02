# Whiffle client

## Installation

`whiffle-client` can be installed with pip in editable mode:

`pip install -e .`

If extra dependencies are needed, they can be installed as follows:

`pip install -e ".[analysis]"`

## Command line interface

### List config

`whiffle config-list`

### Add token to config

`whiffle config login`

This will open interactive browser portal where user/password log in can be done. From there, token will be automatically stored on local configuration for further usage.

### Change url to staging (production by default)

`whiffle config-edit whiffle.url https://staging.whs.whiffle.cloud`

### Run a task

`whiffle run whiffle_client/resources/example_generic_params.json`


## Testing

### Build and run unit tests

`docker build --rm . -t whiffle-client && docker run --rm whiffle-client pytest`

### Build and run container interactively

`docker build --rm . -t whiffle-client && docker run --rm -it whiffle-client bash`

## Deploying

`bash
docker build --rm . -t whiffle-client && docker run --rm -it whiffle-client bash
python -m build
python3 -m twine upload --repository pypi dist/*
`