# Using Prefect with Django

This project contains an example Django application configured
to use [Prefect 2.0](https://prefect.io) for workflows and tasks.

## Project structure

The repository is laid out as a top-level folder
containing the root of the  `myapi` Django application.

In the usual fashion, the application contains an app for
the site, named `myapi`. The `workflows` app contains
Prefect flows.

```
.
├── README.md
├── db.sqlite3
├── manage.py
├── myapi
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── requirements.txt
├── setup.py
└── workflows
    ├── __init__.py
    ├── apps.py
    ├── management
    │   └── commands
    │       └── prefectcli.py
    ├── test_flow-deployment.yaml
    ├── test_flow.py
    └── tests.py
```

The important parts for our consideration are:

- The Prefect flow: `myapi/workflows/test_flow.py`
- An example Deployment definition for the flow: `myapi/workflows/test_flow-deployment.py`
- A Django management command for running Prefect CLI commands within a Django environment: `myapi/workflows/management/commands/prefectcli.py`
- Django views that demonstrate how to run the flow: `myapi/myapi/views.py`

You can read these files in depth to see how they work. This README will
walk you through _using_ the bundled management command and example Django
views.

## Setup

Django applications do not normally have to be installed into a Python
environment. However, the Prefect flow in this example needs access to
your Django code on the Python path. The most straightforward way to
ensure that this is the case is to install the Django application.

NOTE: This README assumes that you have created a Python environment for
this example, using virtualenv, Conda, or another tool of your choice, and
does not include instructions on how to do so.

In the project's root directory, run the following  `pip install` command
to install the Django application in editable mode:

pip install -e .
This installs the two Django "apps" in the project, `myapi` and `workflows`,
into your Python environment. It also installs the project's dependencies.

Next, **set up Django**. This example assumes you are familiar with the setup
that Django requires, like running initial migrations and creating a superuser.

**NOTE**: You will need at least one user in your database for this example to
work!

## Run Prefect and Django

For this example, you should have a Prefect API server running.

NOTE: This example project includes a management command, `prefectcli`, that
runs any Prefect CLI command. For consistency, this README will use the
`prefectcli` wrapper for all Prefect commands.

Run the server like this:

./manage.py prefectcli orion start
In yet another terminal, start the Django API:

./manage.py runserver
OK! Don't try to use the API yet. Before we do that, we're going to create a
Deployment for the example flow.

## Create a Deployment

This example includes an example Deployment YAML file in
`workflows/example-deployment.yaml`, but this is just so you can see a working
file. **You will need to build your own Deployment YAML for this example.**

You should build your own Deployment YAML by running the following command
from the root of the project:

./manage.py prefectcli deployment build workflows/test_flow.py:test_flow --name test-flow
The output will be a YAML file. You can check it out if you want, but you
can also just _apply_ it -- this sets up your new Deployment in the Prefect
API:

./manage.py prefectcli deployment apply test_flow-deployment.yaml
NOTE: Remember to apply **your** YAML file -- the YAML file that you just
built with the `build` command, not the example YAML file.

## Start the Prefect Agent

Once you have the Prefect API running and have created a Deployment, you can
start the Prefect Agent.

In a new terminal, run the following command:

./manage.py prefectcli agent start -q default
You should now have three processes running:

- The Django development server
- The Prefect API
- The Prefect agent

Now, you're ready to run some flows!

## Running flow immediately

You can run a Prefect flow immediately by calling it. Let's see how this works
from a Django view.

### The code

If you look in the file `myapi/views.py`, you'll see the following Django view:

```python
from django.http import HttpResponse

from workflows.test_flow import test_flow


def run_flow_immediately(request):
    """
    Calling a flow runs it in the current Python process, which may not be what
    you want during a web request but is still possible.
    """
    test_flow()
    return HttpResponse(status=200)
```

This view imports the Prefect flow `test_flow` and calls it. Doing so runs the
flow immediately in the current Python process, which means that the flow will
run to completion before the Django view returns an HTTP response.

### Seeing it work

To see how this works, open a browser and visit: http://localhost:8000/run_flow_immediately

**NOTE**: You should still have the processes we started earlier running,
e.g. the Django development server, Prefect API, and Prefect agent.

Now check your Django server output. You should see something like this:

```
00:43:41.622 | INFO    | prefect.engine - Created flow run 'conscious-tuna' for flow 'test-flow'
Hello! andrew
00:43:41.772 | INFO    | Flow run 'conscious-tuna' - Finished in state Completed()
[14/Oct/2022 00:43:41] "GET /run_flow_immediately HTTP/1.1" 200 0
```

What happened? Your flow ran in the server process. It finished, and then
Django returned an HTTP response.

## Scheduling a flow run

What you _probably_ want to do in a web request is schedule a flow to run
"at some time" and return an HTTP response to the user without waiting for
the flow run to complete. Let's see how to do that from a Django view.

### The code

You can schedule a flow to run outside the current Python process using
a Deployment. Once you've created a deployment for your flow, you can use
the `run_deployment()` helper to schedule a flow run.

Once again in the `myapi/views.py` file, you'll see the following Django view:

```python
from django.http import HttpResponse

from prefect.deployments import run_deployment


def schedule_flow_run(request):
    """
    Once a deployment exists for your flow, you can use `run_deployment()` to
    schedule a flow run.
  
    By default, `run_deployment()` will wait for the flow run to complete
    before returning. However, if you set `timeout=0`, the function returns
    immediately: the Django web request continues, and sometime later, your
    Prefect agent process will run the flow.
    """
    run_deployment('test-flow/test-flow', timeout=0)
    return HttpResponse(status=200)
```

### Seeing it work

That's exactly what will happen if you visit
the following URL: http://localhost:8000/schedule_flow_run

If you check out the console output for your running Prefect agent, you should
see something like this:

```
./manage.py prefectcli agent start -q default
Starting v2.6.0 agent connected to http://localhost:4200/api...

  ___ ___ ___ ___ ___ ___ _____     _   ___ ___ _  _ _____
 | _ \ _ \ __| __| __/ __|_   _|   /_\ / __| __| \| |_   _|
 |  _/   / _|| _|| _| (__  | |    / _ \ (_ | _|| .` | | |
 |_| |_|_\___|_| |___\___| |_|   /_/ \_\___|___|_|\_| |_|


Agent started! Looking for work from queue(s): default...
00:48:11.140 | INFO    | prefect.agent - Submitting flow run '23df07af-2f29-4997-8db2-5051d6c9b2c7'
00:48:11.212 | INFO    | prefect.infrastructure.process - Opening process 'grumpy-lemur'...
00:48:11.217 | INFO    | prefect.agent - Completed submission of flow run '23df07af-2f29-4997-8db2-5051d6c9b2c7'
00:48:24.331 | INFO    | Flow run 'grumpy-lemur' - Finished in state Completed()
Hello! andrew
00:48:26.706 | INFO    | prefect.infrastructure.process - Process 'grumpy-lemur' exited cleanly.
```

That's your Prefect flow running in the agent process -- not in your web request! Just the way it should be. 😎
