from unittest.mock import patch

import pytest
from django.contrib.admin import AdminSite
from django.contrib.messages import get_messages, storage
from rest_framework import status
from rest_framework.test import APIRequestFactory
from wbcore.test.utils import get_or_create_superuser
from wbintegrator_office365.admin import SubscriptionAdmin, TenantUserAdmin
from wbintegrator_office365.factories import TenantUserFactory
from wbintegrator_office365.models import Subscription, TenantUser


@pytest.mark.django_db
class TestAdmin:
    @pytest.fixture()
    def fixture_request(self):
        request = APIRequestFactory().get("")
        request.session = {}  # for sessions middleware
        request._messages = storage.default_storage(request)  # for messages middleware
        request.user = get_or_create_superuser()
        return request

    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI._get_access_token")
    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI.users")
    def test_admin_fetch_tenantusers(self, mock_users, mock_access_token, fixture_request):
        data = [
            {
                "id": "87d349ed-44d7-43e1-9a83-5f2406dee5bd",
                "display_name": "contoso1",
                "email": "contoso1_gmail.com#EXT#@microsoft.onmicrosoft.com",
            }
        ]
        mock_users.return_value.status_code = status.HTTP_200_OK
        mock_users.return_value = data

        mock_access_token.return_value.status_code = status.HTTP_200_OK
        mock_access_token.return_value = "FAKE_TOKEN"

        TenantUserFactory()
        mma = TenantUserAdmin(TenantUser, AdminSite())

        storages = get_messages(fixture_request)
        assert len(storages) == 0

        response = mma._fetch_tenantusers(fixture_request)

        storages = get_messages(fixture_request)
        assert len(storages) == 1
        assert mock_users.call_count == 1
        assert response.status_code == status.HTTP_302_FOUND

    def test_disable_selected_subscriptions(self, subscription_factory, fixture_request):
        obj = subscription_factory()
        mma = SubscriptionAdmin(TenantUser, AdminSite())
        storages = get_messages(fixture_request)
        assert len(storages) == 0
        assert obj.is_enable is True
        mma.disable_selected_subscriptions(fixture_request, Subscription.objects.all())
        obj.refresh_from_db()
        assert obj.is_enable is False

        storages = get_messages(fixture_request)
        assert len(storages) == 1

    def test_verification_selected_subscriptions(self, subscription_factory, fixture_request):
        obj = subscription_factory()
        mma = SubscriptionAdmin(TenantUser, AdminSite())
        storages = get_messages(fixture_request)
        assert len(storages) == 0
        assert obj.is_enable is True
        mma.verification_selected_subscriptions(fixture_request, Subscription.objects.all())

        storages = get_messages(fixture_request)
        assert len(storages) == 1

    def test_renew_selected_subscriptions(self, subscription_factory, fixture_request):
        obj = subscription_factory()
        mma = SubscriptionAdmin(TenantUser, AdminSite())
        storages = get_messages(fixture_request)
        assert len(storages) == 0
        assert obj.is_enable is True
        mma.renew_selected_subscriptions(fixture_request, Subscription.objects.all())

        storages = get_messages(fixture_request)
        assert len(storages) == 1
