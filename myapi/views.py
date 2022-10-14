from django.http import HttpResponse

from prefect.deployments import run_deployment
from workflows.test_flow import test_flow


def run_flow_immediately(request):
    """
    Calling the flow would run it in-process, which may not be what you
    want during a web request but is possible.
    """
    test_flow()
    return HttpResponse(status=200)


def schedule_flow_run(request):
    """
    Instead, you should build and apply a Deployment for your flow. Once
    you've done that, you can use `run_deployment()` to schedule a flow
    run. This is a fire-and-forget action: you can continue the web
    request, and sometime later, your Prefect agent process will run the
    flow.
    """
    run_deployment('test-flow/test-flow')
    return HttpResponse(status=200)
