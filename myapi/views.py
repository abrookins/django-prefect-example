from django.http import HttpResponse

from prefect.deployments import run_deployment
from workflows.test_flow import test_flow


def run_flow_immediately(request):
    """
    Calling a flow runs it in-process, which may not be what you want
    during a web request but is still possible.
    """
    test_flow()
    return HttpResponse(status=200)


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
