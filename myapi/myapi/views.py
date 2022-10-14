from django.http import HttpResponse

from prefect.deployments import run_deployment


def create_flow_run(request):
    # test_flow()
    run_deployment('test-flow/test-flow')
    return HttpResponse(status=200)
