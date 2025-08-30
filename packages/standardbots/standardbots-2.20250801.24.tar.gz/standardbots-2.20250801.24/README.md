You can test the API by using the playground, add your own file or use the
existing python scripts. When a client has an issue, and they send their code.
It's helpful to test their code to see possible issues

# ENABLE API ON YOUR LOCAL MACHINE

Follow the steps here
https://www.notion.so/standardbots/Using-the-REST-API-b2c778d47969444dac61483f0117acad

# CONFIG

At the top of the file, use your token

# RUN

To run a script move into the `sdks/python` folder and run
`python playground/filename.py`

# To create a test build

1. Update version in `setup.py`
2. Run `python3 setup.py sdist bdist_wheel`

# Tests

## `botctl` commands

You may now use the `botctl` commands to setup and run tests.

Set up the testing environment on the computer where you are running the tests:

```bash
# Setup testing environment
botctl publicapi test:setup --help

# Run tests
botctl publicapi test --help
```

Set up the bot environment on the robot:

```bash
botctl publicapi test:setup-bot
```

## Setup

To set up tests:

```bash
cd sdks/python
```

Note: Make sure to select proper python interpreter. Sometimes there is an error
related to missing "dotenv" module, to solve this install it separately

```
python3 -m pip install python-dotenv
python3 -m pip install -r requirements-dev.txt
```

### Create sample data

#### Sample routine

You need to add the sample routine in
[sdks/python/tests/fixtures/test_public_api_routine.json](./tests/fixtures/test_public_api_routine.json)
to your target test environment (i.e. upload the routine to ).

The name of routine should be "Test Public API"

#### Sample globals

- _Variable._ Add global variable called "test_public_api_global" with any
  value.
- _Space._ Create a global space called "Test global space" of any kind.

## Running

Here is a basic test command:

```bash
SB_API_URL=http://34.162.0.32:3000
SB_API_TOKEN=...

python3 -m pytest ./tests --cov=standardbots --token=$SB_API_TOKEN --api-url=$SB_API_URL
```

You may also set up a `.env` file at `sdks/python/.env` with the following
contents:

```bash
export SB_API_URL=http://34.162.0.32:3000
export SB_API_TOKEN=...
```

Then you can just do:

```bash
python3 -m pytest ./tests --cov=standardbots
```

### Robot state and testing (Markers)

We need the bot to be in a certain state to run certain tests. For example, we
need a routine to be running in order to stop the routine. Camera should be
disconnected by default.

At start of testing, robot should:

- _NOT_ be e-stopped.

The basic idea here is:

- These special tests will not be run by default.
- You may pass a flag (e.g. `--camera-connected`) when the bot is in the correct
  state to run the tests.
- Markers usage:
- When `--gripper=<type>` flag is passed(`type` is value from `GripperKindEnum`
  enum):
  1. Tests expect that this specific gripper is connected
  2. Tests without the flag are not run.
- When `--camera-connected` flag is passed:
  1. Tests with the flag are run.
  2. Tests without the flag are not run.

We use [pytest markers](https://docs.pytest.org/en/7.1.x/example/markers.html)
to do this.

#### Camera disconnected

The wrist camera should be disabled. Then run:

```bash
python3 -m pytest ./tests --cov=standardbots --camera-connected
```

#### E-stop

No marker needed for e-stop. However, we do rely on active recovery of e-stop
and getting the failure state in order to do these tests.

When e-stop test runs, cannot have bot in a failure state (pre-test will fail).

## Troubleshooting

### Tests are hanging

The first test appears to start but then nothing happens for several seconds:

```bash
$ python3 -m pytest ./tests --cov=standardbots
========================================================================================================== test session starts ===========================================================================================================
platform linux -- Python 3.10.12, pytest-6.2.5, py-1.10.0, pluggy-0.13.0
rootdir: /workspaces/sb/sdks/python, configfile: pytest.ini
plugins: ament-pep257-0.12.11, ament-xmllint-0.12.11, launch-testing-1.0.6, launch-testing-ros-0.19.7, ament-flake8-0.12.11, ament-lint-0.12.11, ament-copyright-0.12.11, colcon-core-0.18.1, cov-6.0.0
collected 110 items

tests/test_apis.py
```

Fixes:

- _Make sure you can log into remote control._ Ensure that botman is connected.
- _Ensure that the robot URL is up-to-date._ Botman url will often change when
  you reboot.

### Custom sensors

To test custom sensors:

- go to the menu on the left bottom corner;
- Click on 'Equipment';
- Add Gripper > Custom Gripper;
- Go to the Sensors tab and click 'Add Sensor';
- Keep the default values as they are (name: 'Sensor 1', kind: 'Control Box IO',
  sensor value: 'low');
- Hit 'Save' and make sure the Custom Gripper is enabled.

Then run:

```bash
python3 -m pytest ./tests --cov=standardbots --gripper=custom_sensors
```

## Database backups

> See command: `botctl publicapi test:setup-bot`.

We now have a common robot database state that can be used for testing. While
this isn't necessary for use, it does provide a common state for testing.

### How to create a new backup

In the place where you are running the stack and want to create the backup (e.g.
on the control box):

```bash
DB_USER=sb
DB_NAME=sb
BACKUP_FILE=$HOME/db-backup-publicapi-test.sql

docker exec -it postgres-bot pg_dump -U $DB_USER -d $DB_NAME -F c -f /tmp/backup.sql

docker cp postgres-bot:/tmp/backup.sql $BACKUP_FILE
```

If you need to download to the actual development environment:

```bash
CB_FILE=/home/control-box-bot/db-backup-publicapi-test.sql
VM_FILE=~/sb/golang/apps/botctl/commands/publicapi/db-backup-publicapi-test.sql

# Move directly to VM:
scp cb2047:$CB_FILE $VM_FILE
```
