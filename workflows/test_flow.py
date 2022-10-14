import django
django.setup()

from django.contrib.auth.models import User
from prefect import flow


@flow
def test_flow():
    user = User.objects.first()
    print(f"Hello! {user.username}")
