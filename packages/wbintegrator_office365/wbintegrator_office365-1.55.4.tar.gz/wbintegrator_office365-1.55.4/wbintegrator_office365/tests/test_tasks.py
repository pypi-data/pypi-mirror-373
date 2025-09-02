from datetime import timedelta
from unittest.mock import patch

import pandas as pd
import phonenumbers
import pytest
from rest_framework import status
from wbcore.contrib.directory.factories import TelephoneContactFactory
from wbintegrator_office365.factories import SubscriptionFactory, TenantUserFactory
from wbintegrator_office365.importer import parse
from wbintegrator_office365.models import CallEvent, Subscription
from wbintegrator_office365.models.event import fetch_tenantusers
from wbintegrator_office365.models.subscription import (
    subscribe,
    unsubscribe,
    verification_subscriptions,
)


# This method will be used by the mock to replace requests.get
class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


@pytest.mark.django_db
class TestTaskSubscription:
    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI._get_access_token")
    @patch("wbintegrator_office365.importer.api.requests.post")
    def test_subscribe(self, mock_post, mock_access_token):
        obj = SubscriptionFactory(type_resource=Subscription.TypeResource.CALLRECORD)
        data = {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#subscriptions/$entity",
            "value": [
                {
                    "id": "7f105c7d-2dc5-4530-97cd-4e7ae6534c07",
                    "resource": "me/mailFolders('Inbox')/messages",
                    "applicationId": "24d3b144-21ae-4080-943f-7067b395b913",
                    "changeType": "created",
                    "clientState": "secretClientValue",
                    "notificationUrl": "https://webhook.azurewebsites.net/api/send/myNotifyClient",
                    "expirationDateTime": "2016-11-20T18:23:45.9356913Z",
                    "creatorId": "8ee44408-0679-472c-bc2a-692812af3437",
                    "latestSupportedTlsVersion": "v1_2",
                }
            ],
        }
        data = parse(pd.json_normalize(data.get("value")))[0]
        mock_access_token.return_value.status_code = status.HTTP_200_OK
        mock_access_token.return_value = "FAKE_TOKEN"

        mock_post.return_value = MockResponse(data, 201)
        assert obj.subscription_id != data.get("id")
        subscribe(obj.id, "/communications/callRecords")
        assert mock_post.call_count == 1
        obj = Subscription.objects.get(id=obj.id)
        assert obj.subscription_id == data.get("id")

    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI.users")
    @patch("wbintegrator_office365.models.subscription.chain")
    def test_post_save_subscription(self, mock_chain, mock_users):
        with patch("wbintegrator_office365.models.event.transaction.on_commit", new=lambda fn: fn()):
            mock_chain.return_value.status_code = 200
            mock_users.return_value.status_code = 200

            tenant = TenantUserFactory()
            mock_users.return_value = [{"id": tenant.tenant_id}]

            assert mock_chain.call_count == 0
            SubscriptionFactory(
                is_enable=True, type_resource=Subscription.TypeResource.CALLRECORD, expiration_date=None
            )
            assert mock_chain.call_count == 1
            SubscriptionFactory(
                subscription_id=None,
                is_enable=True,
                tenant_user=tenant,
                type_resource=Subscription.TypeResource.CALENDAR,
            )
            assert mock_chain.call_count == 1

    @pytest.mark.parametrize("type_resource", ["CALLRECORD", "CALENDAR"])
    @patch("wbintegrator_office365.models.subscription.chain")
    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI.users")
    @patch("requests.patch")
    def test_resubscribe(self, mock_patch, mock_users, mock_chain, type_resource):
        if type_resource == Subscription.TypeResource.CALLRECORD:
            obj = SubscriptionFactory(is_enable=True, type_resource=Subscription.TypeResource.CALLRECORD)
        else:
            mock_users.return_value.status_code = 200
            tenant = TenantUserFactory()
            mock_users.return_value = [{"id": tenant.tenant_id}]
            obj = SubscriptionFactory(
                is_enable=True, tenant_user=tenant, type_resource=Subscription.TypeResource.CALENDAR
            )
        data = {"expiration": obj.expiration_date + timedelta(days=2), "notification_url": "fake_url"}
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = data

        assert mock_patch.call_count == 0
        obj.resubscribe()
        assert mock_patch.call_count == 1

        obj = Subscription.objects.get(id=obj.id)
        assert obj.expiration_date == data.get("expiration")

    @patch("wbintegrator_office365.models.subscription.chain")
    @patch("requests.get")
    def test_verification_subscriptions(self, mock_get, mock_chain):
        with patch("wbintegrator_office365.models.event.transaction.on_commit", new=lambda fn: fn()):
            data = {"value": [{"id": "fake_id"}]}
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = data

            obj = SubscriptionFactory(
                expiration_date=None, type_resource="CALLRECORD", is_enable=True, subscription_id="fake_id"
            )
            obj2 = SubscriptionFactory(
                subscription_id=None, type_resource="CALENDAR", is_enable=True, tenant_user=TenantUserFactory()
            )
            obj2.subscription_id = "other_fake_id"
            obj2.save()

            assert mock_chain.call_count == 1
            assert mock_get.call_count == 0
            verification_subscriptions(obj.id)
            assert mock_get.call_count == 1
            verification_subscriptions(obj2.id)
            assert mock_get.call_count == 2

            assert Subscription.objects.get(id=obj.id).is_enable is True
            assert Subscription.objects.get(id=obj2.id).is_enable is False

    @patch("requests.delete")
    def test_unsubscribe(self, mock_delete):
        mock_delete.return_value.status_code = 204
        obj = SubscriptionFactory(is_enable=True)
        assert mock_delete.call_count == 0
        unsubscribe(obj.id)
        assert mock_delete.call_count == 1


data = {
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#communications/callRecords/$entity",
    "version": 1,
    "type": "peerToPeer",
    "modalities": ["audio"],
    "lastModifiedDateTime": "2020-02-25T19:00:24.582757Z",
    "startDateTime": "2020-02-25T18:52:21.2169889Z",
    "endDateTime": "2020-02-25T18:52:46.7640013Z",
    "id": "e523d2ed-2966-4b6b-925b-754a88034cc5",
    "organizer": {
        "user": {
            "id": "821809f5-0000-0000-0000-3b5136c0e777",
            "displayName": "Abbie Wilkins",
            "tenantId": "dc368399-474c-4d40-900c-6265431fd81f",
        }
    },
    "participants": [
        {
            "user": {
                "id": "821809f5-0000-0000-0000-3b5136c0e777",
                "displayName": "Abbie Wilkins",
                "tenantId": "dc368399-474c-4d40-900c-6265431fd81f",
            }
        },
        {
            "user": {
                "id": "f69e2c00-0000-0000-0000-185e5f5f5d8a",
                "displayName": "Owen Franklin",
                "tenantId": "dc368399-474c-4d40-900c-6265431fd81f",
            }
        },
    ],
}

data_with_guest_user = {
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#communications/callRecords/$entity",
    "version": 1,
    "type": "peerToPeer",
    "modalities": ["audio"],
    "lastModifiedDateTime": "2020-02-25T19:00:24.582757Z",
    "startDateTime": "2020-02-25T18:52:21.2169889Z",
    "endDateTime": "2020-02-25T18:52:46.7640013Z",
    "id": "e523d2ed-2966-4b6b-925b-754a88034cc5",
    "organizer": {
        "user": {
            "id": "821809f5-0000-0000-0000-3b5136c0e777",
            "displayName": "Abbie Wilkins",
            "tenantId": "dc368399-474c-4d40-900c-6265431fd81f",
        }
    },
    "participants": [
        {
            "user": None,
            "acsUser": None,
            "spoolUser": None,
            "phone": None,
            "guest": {"id": "c6f4f18f1e99401a9193fbf954f6e903", "displayName": "Guest user", "tenantId": None},
            "encrypted": None,
            "onPremises": None,
            "acsApplicationInstance": None,
            "spoolApplicationInstance": None,
            "applicationInstance": None,
            "application": None,
            "device": None,
        },
        {
            "acsUser": None,
            "spoolUser": None,
            "phone": None,
            "guest": None,
            "encrypted": None,
            "onPremises": None,
            "acsApplicationInstance": None,
            "spoolApplicationInstance": None,
            "applicationInstance": None,
            "application": None,
            "device": None,
            "user": {
                "id": "303eecac-5bf1-44df-96c2-2aae187d46d1",
                "displayName": "External user",
                "tenantId": "9692a3d3-2a08-4ec8-a0bd-1db355eb4230",
            },
        },
    ],
}

data_with_guest_organiser = {
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#communications/callRecords/$entity",
    "version": 1,
    "type": "peerToPeer",
    "modalities": ["audio"],
    "lastModifiedDateTime": "2020-02-25T19:00:24.582757Z",
    "startDateTime": "2020-02-25T18:52:21.2169889Z",
    "endDateTime": "2020-02-25T18:52:46.7640013Z",
    "id": "e523d2ed-2966-4b6b-925b-754a88034cc5",
    "organizer": {
        "user": None,
        "guest": {
            "id": "821809f5-0000-0000-0000-3b5136c0e777",
            "displayName": "Abbie Wilkins",
            "tenantId": "dc368399-474c-4d40-900c-6265431fd81f",
        },
    },
    "participants": [],
}

data_with_phone_organiser = {
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#communications/callRecords/$entity",
    "version": 1,
    "type": "peerToPeer",
    "modalities": ["audio"],
    "lastModifiedDateTime": "2020-02-25T19:00:24.582757Z",
    "startDateTime": "2020-02-25T18:52:21.2169889Z",
    "endDateTime": "2020-02-25T18:52:46.7640013Z",
    "id": "e523d2ed-2966-4b6b-925b-754a88034cc5",
    "organizer": {
        "user": None,
        "guest": None,
        "phone": {"id": "+41223178146", "displayName": "None", "tenantId": "None"},
    },
    "participants": [],
}


@pytest.mark.django_db
class TestTasksCall:
    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI.users")
    def test_fetch_tenantusers(self, mock_users):
        data = [
            {
                "id": "87d349ed-44d7-43e1-9a83-5f2406dee5bd",
                "display_name": "contoso1",
                "email": "contoso1_gmail.com#EXT#@microsoft.onmicrosoft.com",
            }
        ]
        mock_users.return_value.status_code = 200
        mock_users.return_value = data
        datum, count_added = fetch_tenantusers()
        assert mock_users.call_count == 1
        assert datum == data
        assert count_added == 1

    @patch("requests.get")
    @pytest.mark.parametrize(
        "data", [data, data_with_guest_user, data_with_guest_organiser, data_with_phone_organiser]
    )
    def test_fetch_call(self, mock_get, data, event_factory):
        event = event_factory(uuid_event="87d349ed-44d7-43e1-9a83-5f2406dee5bd")
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = parse(pd.json_normalize(data))

        assert CallEvent.objects.count() == 0
        event.fetch_call()
        assert mock_get.call_count == 1
        assert CallEvent.objects.count() == 1

    @patch("requests.get")
    @pytest.mark.parametrize("data", [data_with_phone_organiser])
    def test_fetch_call_phone(self, mock_get, data, event_factory):
        event = event_factory(uuid_event="87d349ed-44d7-43e1-9a83-5f2406dee5bd")
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = parse(pd.json_normalize(data))

        my_number = "+41 22 317 81 46"
        parser_number = phonenumbers.parse(my_number, "CH")
        phone_numbers = phonenumbers.format_number(parser_number, phonenumbers.PhoneNumberFormat.E164)
        TelephoneContactFactory(number=phone_numbers)

        assert CallEvent.objects.count() == 0
        event.fetch_call()
        assert mock_get.call_count == 1
        assert CallEvent.objects.count() == 1
