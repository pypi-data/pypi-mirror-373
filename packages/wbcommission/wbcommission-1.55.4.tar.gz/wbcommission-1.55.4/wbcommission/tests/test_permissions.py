import pytest
from django.contrib.auth.models import Permission
from faker import Faker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from wbcore.contrib.authentication.factories import UserFactory
from wbcore.contrib.authentication.models import User
from wbcore.tests.test_permissions.test_backend import create_internal_user

from wbcommission.permissions import IsCommissionAdmin

fake = Faker()


@pytest.mark.django_db
class TestPermissionClass:
    @pytest.fixture()
    def admin_user(self):
        user = UserFactory.create()
        user.user_permissions.add(
            Permission.objects.get(content_type__app_label="wbcommission", codename="administrate_commission")
        )
        return User.objects.get(id=user.id)

    def test_normal_user_permission(self, rf, user):
        rf.user = user
        assert not IsCommissionAdmin().has_permission(rf, None)

    def test_admin_permission(self, rf, admin_user):
        rf.user = admin_user
        assert IsCommissionAdmin().has_permission(rf, None)

    def test_recompute_only_for_admin(self, user, admin_user):
        client = APIClient()
        url = reverse("wbcommission:rebate-recompute")

        client.force_authenticate(user=user)
        response = client.patch(url, data={"start_date": fake.date_object()})
        assert response.status_code == 403

        client.force_authenticate(user=admin_user)
        response = client.patch(url, data={"start_date": fake.date_object()})
        assert response.status_code == 200

    def test_auditreport_only_for_admin(self, user, admin_user, company):
        client = APIClient()
        url = reverse("wbcommission:rebate-auditreport")

        client.force_authenticate(user=user)
        response = client.patch(url + f"?recipient_id={company.id}")
        assert response.status_code == 403

        client.force_authenticate(user=admin_user)
        response = client.patch(url + f"?recipient_id={company.id}")
        assert response.status_code == 200

    def test_customerreport_only_for_internaluser(self, user, admin_user, company):
        client = APIClient()
        url = reverse("wbcommission:rebate-customerreport")

        client.force_authenticate(user=user)
        response = client.patch(url + f"?recipient_id={company.id}")
        assert response.status_code == 403

        client.force_authenticate(user=create_internal_user())
        response = client.patch(url + f"?recipient_id={company.id}")
        assert response.status_code == 200
