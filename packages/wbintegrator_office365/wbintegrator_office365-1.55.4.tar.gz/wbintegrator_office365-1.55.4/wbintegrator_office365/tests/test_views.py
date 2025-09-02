from datetime import timedelta
from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from wbcore.contrib.authentication.factories import InternalUserFactory
from wbcore.test.utils import get_or_create_superuser
from wbhuman_resources.factories import EmployeeHumanResourceFactory
from wbintegrator_office365.factories import CallEventFactory, CallUserFactory
from wbintegrator_office365.viewsets.viewsets import (
    CallEventReceptionTime,
    CallEventSummaryGraph,
    callback_consent_permission,
    listen,
)


@pytest.mark.django_db
class TestView:
    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (CallEventReceptionTime, CallEventFactory),
            (CallEventSummaryGraph, CallEventFactory),
        ],
    )
    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI._get_access_token")
    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI.users")
    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI.get_calendar_event")
    def test_option_request(self, mock_calendar_event, mock_users, mock_acess, mvs, factory):
        request = APIRequestFactory().options("")
        request.user = get_or_create_superuser()
        factory()
        kwargs = {"user_id": request.user.id}
        vs = mvs.as_view({"options": "options"})
        response = vs(request, **kwargs)
        assert response.status_code == status.HTTP_200_OK
        assert response.data

    @pytest.mark.parametrize(
        "mvs, factory",
        [
            (CallEventReceptionTime, CallEventFactory),
            (CallEventSummaryGraph, CallEventFactory),
        ],
    )
    def test_get_plotly(self, mvs, factory):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()
        _mvs = mvs(request=request)
        fig = _mvs.get_plotly(_mvs.queryset)
        assert fig

        factory()
        _mvs = mvs(request=request)
        fig = _mvs.get_plotly(_mvs.queryset)
        assert fig

    @pytest.mark.parametrize(
        "mvs, factory, empty_compare_employee",
        [(CallEventSummaryGraph, CallEventFactory, True), (CallEventSummaryGraph, CallEventFactory, False)],
    )
    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI._get_access_token")
    @patch("wbintegrator_office365.importer.MicrosoftGraphAPI.users")
    def test_get_plotly_CallEventSummaryGraph(self, mock_users, mock_acess, mvs, factory, empty_compare_employee):
        request = APIRequestFactory().get("")
        request.user = get_or_create_superuser()

        obj = factory(is_internal_call=True)
        obj.end = obj.start + timedelta(seconds=60)
        person = InternalUserFactory().profile
        employee = EmployeeHumanResourceFactory(profile=person)

        if not empty_compare_employee:
            call_user = CallUserFactory(tenant_user__profile=person)
            factory(start=obj.start, end=obj.end, type=obj.type, is_internal_call=True, participants=(call_user,))

        request.GET = request.GET.copy()
        request.GET["compare_employee"] = employee.id
        request.GET["start"] = str(obj.start.date())
        request.GET["end"] = str(obj.end.date() + timedelta(days=30))
        request.GET["call_duration"] = (obj.end - obj.start).total_seconds()
        request.GET["call_type"] = obj.type
        request.GET["call_area"] = obj.is_internal_call
        request.GET["business_day_without_call"] = "true"
        _mvs = mvs(request=request)
        fig = _mvs.get_plotly(_mvs.get_queryset())
        assert fig

    @pytest.mark.parametrize("view", [callback_consent_permission])
    def test_callback_consent_permission(self, view):
        factory = APIRequestFactory()
        request = factory.get("")
        response = view(request)
        assert response.status_code == status.HTTP_200_OK

    data = {
        "value": [
            {
                "change_type": "created",
                "subscription_id": "82507f73-75c5-4295-8ac4-5bf55f38541f",
                "resource": "communications/callRecords/af419444-a189-499c-967b-1aae574b2cc1",
                "resource_data": {"id": "af419444-a189-499c-967b-1aae574b2cc1"},
            }
        ]
    }

    @patch("wbintegrator_office365.models.event.handle_event_from_webhook.delay")
    @pytest.mark.parametrize(
        "view, validation_token, request_body",
        [(listen, None, None), (listen, "validationToken", None), (listen, None, data)],
    )
    def test_listen(self, handle_event, view, validation_token, request_body, event_factory):
        with patch("wbintegrator_office365.viewsets.viewsets.transaction.on_commit", new=lambda fn: fn()):
            factory = APIRequestFactory()
            request = factory.post("", request_body, format="json")
            if validation_token:
                request.GET = request.GET.copy()
                request.GET["validationToken"] = "fake_validation_token"
            assert handle_event.call_count == 0
            for i in range(1, 3):
                response = view(request)
                if request_body:
                    assert handle_event.call_count == i
                else:
                    assert handle_event.call_count == 0
            assert response.status_code == status.HTTP_200_OK
