# Cave Utilities for the Cave App
[![PyPI version](https://badge.fury.io/py/cave_utils.svg)](https://badge.fury.io/py/cave_utils)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
Basic utilities for the MIT Cave App.
This package is intended to be used by the Cave App and the Cave API.

## Overview

This package is part of the larger [Cave App](https://github.com/MIT-CAVE/cave_app) framework. It provides utilities that are commonly used across different Cave applications, such as validation and logging. It is designed to be an easy to integrate library that can be used in any Cave application. It also serves to provide automated documentation and testing.

You can find the low level documentation for this package [here](https://mit-cave.github.io/cave_utils/index.html).



## Setup

Make sure you have Python 3.11.x (or higher) installed on your system. You can download it [here](https://www.python.org/downloads/).

### Installation

```
pip install cave_utils
```

# cave_utils development

## Running Tests, Prettifying Code, and Updating Docs

Make sure Docker is installed and running.

- Create a docker container and drop into a shell
    - `./run.sh`
- Run all tests (see ./utils/test.sh)
    - `./run.sh test`
- Prettify the code (see ./utils/prettify.sh)
    - `./run.sh prettify`
- Update the docs (see ./utils/docs.sh)
    - `./run.sh docs`

- Note: You can and should modify the `Dockerfile` to test different python versions.

### Using Local Hotloading With a Cave App

1. In your `cave_app`, update the following file:

    `utils/run_server.sh`
    ```
    #!/bin/bash

    SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
    APP_DIR=$(dirname "$SCRIPT_DIR")

    pip install -e /cave_utils

    source ./utils/helpers/shell_functions.sh
    source ./utils/helpers/ensure_postgres_running.sh
    # Check if the app is functional before proceeding
    if [ "$(python ./manage.py check --deployment_type development | grep "System check identified no issues" | wc -l)" -eq "0" ]; then
    printf "Unable to start the app due to an error in the code. See the stacktrace above." 2>&1 | pipe_log "ERROR"
    rm -r "./tmp"
    exit 1
    fi
    source ./utils/helpers/ensure_db_setup.sh

    python "$APP_DIR/manage.py" runserver 0.0.0.0:8000 2>&1 | pipe_log "INFO"
    ```

2. Remove `cave_utils` from the root `requirements.txt` file

3. In your `cave_app`, set `LIVE_API_VALIDATION_PRINT=True` in the `.env` file
    - This will validate your data every time an API command is called for each session

4. Use the following command to run your `cave_app`:
    `cave run --docker-args "--volume {local_path_to_cave_utils}/cave_utils:/cave_utils"`
    - As you edit `cave_utils`, any changes will be hotloaded into your running `cave_app`

### Using interactive mode in your Cave App and running tests

- Note: This is for very specific use cases, such as running tests or debugging in an interactive shell.
- Note: In general, we copy all included examples from the cave_app to the `cave_utils/test/api_examples` directory, so you can run tests against them without needing to run the cave_app.
    - These copied examples can be tested by running `./run.sh test` in the cave_utils directory, which will run all tests in the `cave_utils/test`.
        - This includes `test_validator.py` which runs all examples in the `cave_utils/test/api_examples` directory


1. Run cave_app in interactive mode mounting cave_utils as a volume:
    `cave run --docker-args "--volume {local_path_to_cave_utils}/cave_utils:/cave_utils" -it`
2. Then install cave utils in the docker container:
    `pip install -e /cave_utils`
3. Then run some tests (eg `validate_all_examples.py`):
    `python cave_api/tests/validate_all_examples.py`


# Generate a New Release

1. Make sure all tests are passing and the code is prettified.
2. Make sure the documentation is up to date.
3. Make sure the version number is updated in `setup.cfg` and `pyproject.toml`.
4. Set up your virtual environment
    - `python3 -m virtualenv venv`
    - `source venv/bin/activate`
    - `pip install -r requirements.txt`
5. Update the release
    - `source venv/bin/activate`
    - `./publish.sh`