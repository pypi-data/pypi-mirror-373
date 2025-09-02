import json
from datetime import timedelta

import pandas as pd
import requests
from django.conf import settings
from django.utils import timezone
from dynamic_preferences.registries import global_preferences_registry
from rest_framework import status

from .parser import parse


class MicrosoftGraphAPI:
    def __init__(self):
        self.authority = getattr(settings, "WBINTEGRATOR_OFFICE365_AUTHORITY", "")
        self.client_id = getattr(settings, "WBINTEGRATOR_OFFICE365_CLIENT_ID", "")
        self.client_secret = getattr(settings, "WBINTEGRATOR_OFFICE365_CLIENT_SECRET", "")
        self.redirect_uri = getattr(settings, "WBINTEGRATOR_OFFICE365_REDIRECT_URI", "")
        self.token_endpoint = getattr(settings, "WBINTEGRATOR_OFFICE365_TOKEN_ENDPOINT", "")
        self.notification_url = getattr(settings, "WBINTEGRATOR_OFFICE365_NOTIFICATION_URL", "")
        self.graph_url = getattr(settings, "WBINTEGRATOR_OFFICE365_GRAPH_URL", "")

        global_preferences = global_preferences_registry.manager()
        if global_preferences["wbintegrator_office365__access_token"] == "0":
            global_preferences["wbintegrator_office365__access_token"] = self._get_access_token()

    def _get_administrator_consent(self):
        url = f"{self.authority}/adminconsent?client_id={self.client_id}&state=12345&redirect_uri={self.redirect_uri}"
        response = self._query(url, access_token=False)
        if response:
            return response
        else:
            raise ValueError("get administrator consent does not return response 200")

    def _get_access_token(self):
        # Get administrator consent
        self._get_administrator_consent()
        # Get an access token
        url = f"{self.authority}{self.token_endpoint}"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "scope": "https://graph.microsoft.com/.default",
            "client_secret": self.client_secret,
        }

        response = self._query(url, method="POST", data=payload, is_json=False, access_token=False)
        data = None
        if response:
            if response.json():
                data = response.json().get("access_token")
        else:
            raise ValueError(response, response.json())
        return data

    def _subscribe(self, resource, minutes, change_type):
        data = {
            "changeType": change_type,
            "notificationUrl": self.notification_url,
            "resource": resource,
            "clientState": "secretClientValue",
            "latestSupportedTlsVersion": "v1_2",
        }
        if minutes:
            # maximum time of subscription 4230 minutes (under 3 days)
            date = timezone.now() + timedelta(minutes=minutes)
            date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
            data["expirationDateTime"] = date

        url = f"{self.graph_url}/subscriptions"
        response = self._query(url, method="POST", data=json.dumps(data))
        data = None
        if response:
            if response.json():
                data = parse(response.json(), scalar_value=True)
                if data:
                    data = data[0]
        else:
            raise ValueError(response, response.json())
        return data

    def _unsubscribe(self, subscription_id):
        url = f"{self.graph_url}/subscriptions/{subscription_id}"
        return self._query(url, method="DELETE")

    def _renew_subscription(self, subscription_id, minutes=4230):
        url = f"{self.graph_url}/subscriptions/{subscription_id}"
        date = timezone.now() + timedelta(minutes=minutes)
        date = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        data = {"expirationDateTime": date}
        response = self._query(url, method="PATCH", data=json.dumps(data))
        data = None
        if response:
            if response.json():
                data = parse(response.json(), scalar_value=True)
                if data:
                    data = data[0]
        else:
            raise ValueError(response, response.json())
        return data

    def subscriptions(self):
        url = f"{self.graph_url}/subscriptions"
        # curl -X GET -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJub25jZSI6IlVUSmxpNTVOcDV1MHVDb3dwTWxpMThIdDdQRDZwV1VkMWNyNlRRYUNlNG8iLCJhbGciOiJSUzI1NiIsIng1dCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyIsImtpZCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC83ZWJhNTBhMi00N2QyLTQxODUtYWIwNy0yYTNjYTE4YzliNzYvIiwiaWF0IjoxNjE4MjE5ODIwLCJuYmYiOjE2MTgyMTk4MjAsImV4cCI6MTYxODIyMzcyMCwiYWlvIjoiRTJaZ1lBaVNGN3ZUS0tGbng4YTk2ak5mNjhFVEFBPT0iLCJhcHBfZGlzcGxheW5hbWUiOiJOb3RpZmljYXRpb25DYWxsVXNlckFwcGxpY2F0aW9uIiwiYXBwaWQiOiJkYjg5ZDYxNi0xYWJlLTQzNTgtYWRmNC0zYzE2ZWY3ZjQ0ZjAiLCJhcHBpZGFjciI6IjEiLCJpZHAiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC83ZWJhNTBhMi00N2QyLTQxODUtYWIwNy0yYTNjYTE4YzliNzYvIiwiaWR0eXAiOiJhcHAiLCJvaWQiOiIyNzNjODI1Yy00YTYyLTQyOWUtODdiZi0zOWYzZDY2ZTMwYWYiLCJyaCI6IjAuQVRvQW9sQzZmdEpIaFVHckJ5bzhvWXliZGhiV2lkdS1HbGhEcmZROEZ1OV9SUEE2QUFBLiIsInJvbGVzIjpbIkFjY2Vzc1Jldmlldy5SZWFkV3JpdGUuTWVtYmVyc2hpcCIsIk1haWwuUmVhZFdyaXRlIiwiVXNlci5SZWFkV3JpdGUuQWxsIiwiRGVsZWdhdGVkUGVybWlzc2lvbkdyYW50LlJlYWRXcml0ZS5BbGwiLCJDYWxlbmRhcnMuUmVhZCIsIk1haWwuUmVhZEJhc2ljLkFsbCIsIkdyb3VwLlJlYWQuQWxsIiwiQWNjZXNzUmV2aWV3LlJlYWRXcml0ZS5BbGwiLCJEaXJlY3RvcnkuUmVhZFdyaXRlLkFsbCIsIkNhbGxSZWNvcmRzLlJlYWQuQWxsIiwiSWRlbnRpdHlVc2VyRmxvdy5SZWFkLkFsbCIsIlVzZXIuSW52aXRlLkFsbCIsIkRpcmVjdG9yeS5SZWFkLkFsbCIsIlVzZXIuUmVhZC5BbGwiLCJVc2VyTm90aWZpY2F0aW9uLlJlYWRXcml0ZS5DcmVhdGVkQnlBcHAiLCJGaWxlcy5SZWFkLkFsbCIsIk1haWwuUmVhZCIsIkNoYXQuUmVhZC5BbGwiLCJVc2VyLkV4cG9ydC5BbGwiLCJJZGVudGl0eVByb3ZpZGVyLlJlYWQuQWxsIiwiQ2FsZW5kYXJzLlJlYWRXcml0ZSIsIklkZW50aXR5Umlza3lVc2VyLlJlYWQuQWxsIiwiQWNjZXNzUmV2aWV3LlJlYWQuQWxsIiwiTWFpbC5TZW5kIiwiVXNlci5NYW5hZ2VJZGVudGl0aWVzLkFsbCIsIkNvbnRhY3RzLlJlYWQiLCJJZGVudGl0eVJpc2tFdmVudC5SZWFkLkFsbCIsIk1haWwuUmVhZEJhc2ljIiwiQ2hhdC5SZWFkQmFzaWMuQWxsIiwiQ2FsbHMuQWNjZXNzTWVkaWEuQWxsIiwiQXBwbGljYXRpb24uUmVhZC5BbGwiLCJSZXBvcnRzLlJlYWQuQWxsIl0sInN1YiI6IjI3M2M4MjVjLTRhNjItNDI5ZS04N2JmLTM5ZjNkNjZlMzBhZiIsInRlbmFudF9yZWdpb25fc2NvcGUiOiJFVSIsInRpZCI6IjdlYmE1MGEyLTQ3ZDItNDE4NS1hYjA3LTJhM2NhMThjOWI3NiIsInV0aSI6Im9ONGJ1anMzaGtlOUVoUTRCTlV6QUEiLCJ2ZXIiOiIxLjAiLCJ4bXNfdGNkdCI6MTU1ODY4MjUxMX0.Jw5jVFFK2HIHXkWpR61eVGdVv-NnwsMBpHDRUur6UXrUlxtPwLAVvaklEILzALUNKAWe2Ic0k737tAq1C10DCkHF3iJ5bXQWTD0yAux1pZrHNYMMJ-bRvAdcuaLys5Amtas8gcYhj8mSpHdiSclW_17TxPDacSjvDwYEFOjgzAUYUtsoR5Q_q2H14QVR-PFd9WreqcOVy4ELNBBUhFdFjmV8Cb0lLUujW5Q0zBniOrwyRN4VYSdGEuyogoCOeICoNBdgwnLjXq6BMv6CLLSpzwEKDp-ikK7SETDd1uyDADYOUg-YuJ_D-ZIiobUNpA4UnBMNpfrUrCDzF84iox0vWA" 'https://graph.microsoft.com/v1.0/subscriptions'
        response = self._query(url)
        data = None
        if response:
            if datum := response.json():
                data = parse(datum.get("value"))
                url = datum.get("@odata.nextLink")
                while url:
                    response = self._query(url)
                    datum = response.json()
                    data += parse(datum.get("value"))
                    url = datum.get("@odata.nextLink")

        else:
            raise ValueError(response, response.json())
        return data

    def user(self, email):
        query_params = {"$select": "id, userPrincipalName, displayName"}
        url = f"{self.graph_url}/users/{email}"
        response = self._query(url, params=query_params)
        data = None
        if response:
            if response.json():
                data = parse(response.json(), scalar_value=True)
                if data:
                    data = data[0]
        else:
            raise ValueError(response, response.json())
        return data

    def users(self, filter_params=True):
        query_params = {
            "$select": "id,displayName,businessPhones,mobilePhone, userPrincipalName, mail,email, mailNickname, givenName, surname, imAddresses"
        }
        url = f"{self.graph_url}/users"
        if filter_params:
            response = self._query(url, params=query_params)
        else:
            response = self._query(url)
        data = None
        if response:
            data = parse(response.json().get("value"))
        else:
            raise ValueError(response, response.json())
        return data

    def call(self, call_id: str, raise_error: bool = False):
        url = f"{self.graph_url}/communications/callRecords/{call_id}"
        response = self._query(url)
        data = None
        if response and (json_data := response.json()):
            data = parse(pd.json_normalize(json_data))
            if data:
                data = data[0]
        elif raise_error:
            raise ValueError(response, response.json())
        return data

    # CREATION CALENDAR
    def create_calendar_group(self, user_id, data):
        url = f"{self.graph_url}/users/{user_id}/calendarGroups"
        return self._query_create(url, data)

    def create_calendar(self, user_id, data, id_calendar_group=None):
        if id_calendar_group:
            url = f"{self.graph_url}/users/{user_id}/calendarGroups/{id_calendar_group}/calendars"
        else:
            url = f"{self.graph_url}/users/{user_id}/calendars"
        return self._query_create(url, data)

    def create_calendar_event(self, user_id, data, id_calendar_group=None, id_calendar=None):
        if id_calendar:
            # A user's calendar in the default calendarGroup.
            url = f"{self.graph_url}/users/{user_id}/calendars/{id_calendar}/events"
            if id_calendar_group:
                # A user's calendar in a specific calendarGroup.
                url = f"{self.graph_url}/users/{user_id}/calendarGroups/{id_calendar_group}/calendars/{id_calendar}/events"
        else:
            # A user's or group's default calendar.
            url = f"{self.graph_url}/users/{user_id}/events"
        return self._query_create(url, data)

    # LIST CALENDAR
    def get_list_calendar_groups(self, user_id):
        url = f"{self.graph_url}/users/{user_id}/calendarGroups"
        return self._query_get_list(url)

    def get_list_calendars(self, user_id, id_calendar_group=None):
        if id_calendar_group:
            url = f"{self.graph_url}/users/{user_id}/calendarGroups/{id_calendar_group}/calendars"
        else:
            url = f"{self.graph_url}/users/{user_id}/calendars"
        # Configure query parameters to modify the results
        # query_params = {
        #     "$select": "subject, organizer, createdDateTime, lastModifiedDateTime, start, end, reminderMinutesBeforeStart, isReminderOn, recurrence,  hasAttachments, importance, location, webLink, attendees",
        #     "$orderby": "createdDateTime DESC",
        # }
        return self._query_get_list(url)

    def get_list_calendar_events(self, user_id, id_calendar=None, id_calendar_group=None):
        if id_calendar:
            # A user's calendar in the default calendarGroup.
            url = f"{self.graph_url}/users/{user_id}/calendars/{id_calendar}/events"
            if id_calendar_group:
                # A user's calendar in a specific calendarGroup.
                url = f"{self.graph_url}/users/{user_id}/calendarGroups/{id_calendar_group}/calendars/{id_calendar}/events"
        else:
            # A user's or group's default calendar.
            url = f"{self.graph_url}/users/{user_id}/events"
        return self._query_get_list(url)

    # GET CALENDAR
    def get_calendar_group(self, user_id, id_calendar_group=None):
        url = f"{self.graph_url}/users/{user_id}/calendarGroups/{id_calendar_group}"
        return self._query_get(url)

    def get_calendar(self, user_id, id_calendar, id_calendar_group=None):
        if id_calendar_group:
            url = f"{self.graph_url}/users/{user_id}/calendarGroups/{id_calendar_group}/calendars/{id_calendar}"
        else:
            url = f"{self.graph_url}/users/{user_id}/calendars/{id_calendar}"
        return self._query_get(url)

    def get_calendar_event(self, user_id, id_event, id_calendar=None, id_calendar_group=None):
        if id_calendar:
            url = f"{self.graph_url}/users/{user_id}/calendars/{id_calendar}/events/{id_event}"
            if id_calendar_group:
                url = f"{self.graph_url}/users/{user_id}/calendargroups/{id_calendar_group}/calendars/{id_calendar}/events/{id_event}"
        else:
            url = f"{self.graph_url}/users/{user_id}/events/{id_event}"

        return self._query_get(url)

    # FORWARD CALENDAR EVENT
    def forward_calendar_event(self, user_id, id_event, data, id_calendar_group=None, id_calendar=None):
        if id_calendar:
            url = f"{self.graph_url}/users/{user_id}/calendars/{id_calendar}/events/{id_event}/forward"
            if id_calendar_group:
                url = f"{self.graph_url}/users/{user_id}/calendargroups/{id_calendar_group}/calendars/{id_calendar}/events/{id_event}/forward"
        else:
            url = f"{self.graph_url}/users/{user_id}/events/{id_event}/forward"
        return self._query_create(url, data)

    def get_calendar_event_by_resource(self, resource):
        url = f"{self.graph_url}/{resource}"
        return self._query_get(url)

    def get_calendar_from_navigation_link(self, url):
        return self._query_get(url)

    # UPDATE CALENDAR
    def update_calendar_group(self, user_id, id_calendar_group, data):
        url = f"{self.graph_url}/users/{user_id}/calendargroups/{id_calendar_group}"
        return self._query_update(url, data)

    def update_calendar(self, user_id, id_calendar, data, id_calendar_group=None):
        if id_calendar_group:
            url = f"{self.graph_url}/users/{user_id}/calendarGroups/{id_calendar_group}/calendars/{id_calendar}"
        else:
            url = f"{self.graph_url}/users/{user_id}/calendars/{id_calendar}"
        return self._query_update(url, data)

    def update_calendar_event(self, user_id, id_event, data, id_calendar=None, id_calendar_group=None):
        if id_calendar:
            url = f"{self.graph_url}/users/{user_id}/calendars/{id_calendar}/events/{id_event}"
            if id_calendar_group:
                url = f"{self.graph_url}/users/{user_id}/calendargroups/{id_calendar_group}/calendars/{id_calendar}/events/{id_event}"
        else:
            url = f"{self.graph_url}/users/{user_id}/events/{id_event}"
        return self._query_update(url, data)

    # DELETE CALENDAR
    def delete_calendar_group(self, user_id, id_calendar_group):
        url = f"{self.graph_url}/users/{user_id}/calendargroups/{id_calendar_group}"
        return self._query_delete(url)

    def delete_calendar(self, user_id, id_calendar, id_calendar_group=None):
        if id_calendar_group:
            url = f"{self.graph_url}/users/{user_id}/calendarGroups/{id_calendar_group}/calendars/{id_calendar}"
        else:
            url = f"{self.graph_url}/users/{user_id}/calendars/{id_calendar}"
        return self._query_delete(url)

    def delete_calendar_event(self, user_id, id_event, id_calendar=None, id_calendar_group=None):
        if id_calendar:
            url = f"{self.graph_url}/users/{user_id}/calendars/{id_calendar}/events/{id_event}"
            if id_calendar_group:
                url = f"{self.graph_url}/users/{user_id}/calendargroups/{id_calendar_group}/calendars/{id_calendar}/events/{id_event}"
        else:
            url = f"{self.graph_url}/users/{user_id}/events/{id_event}"
        return self._query_delete(url)

    def delete_calendar_event_by_resource(self, resource):
        url = f"{self.graph_url}/{resource}"
        return self._query_delete(url)

    def get_or_create_workbench_calendar(self, user_id, calendar_name):
        workbench_calendar = None
        datum = self.get_list_calendars(user_id=user_id)
        if calendar_name:
            calendars = {calendar.get("name"): calendar.get("id") for calendar in datum}
            if calendar_name in calendars.keys():
                workbench_calendar = self.get_calendar(user_id, calendars[calendar_name])
            else:
                data = {"name": calendar_name}
                workbench_calendar = self.create_calendar(user_id, data)
        else:
            for calendar in datum:
                if calendar.get("is_default_calendar") is True:
                    workbench_calendar = self.get_calendar(user_id, calendar.get("id"))
        return workbench_calendar

    def _query_get_list(self, url):
        response = self._query(url)
        datum = None
        if response:
            if response.json():
                if response.json().get("value"):
                    datum = parse(pd.json_normalize(response.json().get("value")))
        else:
            raise ValueError(response, response.json())
        return datum

    def _query_get(self, url, raise_error=False):
        response = self._query(url)
        data = None
        if response:
            if response.json():
                data = parse(pd.json_normalize(response.json()))
                if data:
                    data = data[0]
        elif raise_error:
            raise ValueError(response, response.json())
        return data

    def _query_create(self, url, data):
        response = self._query(url, method="POST", data=json.dumps(data))
        data = None
        if response.status_code < 400:
            try:
                if response.json():
                    data = parse(pd.json_normalize(response.json()))
                    if data:
                        data = data[0]
            except requests.exceptions.InvalidJSONError:
                pass  # print(response, response.__dict__)

        else:
            raise ValueError(response, response.__dict__)
        return data

    def _query_update(self, url, data):
        response = self._query(url, method="PATCH", data=json.dumps(data))
        data = None
        if response:
            if response.json():
                data = parse(pd.json_normalize(response.json()))
        else:
            if response.status_code not in [status.HTTP_503_SERVICE_UNAVAILABLE, status.HTTP_409_CONFLICT]:
                raise ValueError(response, response.json())
            else:
                import time

                time.sleep(60)
                if response := self._query(url, method="PATCH", data=json.dumps(data)):
                    if response.json():
                        data = parse(pd.json_normalize(response.json()))
        return data

    def _query_delete(self, url):
        response = self._query(url, method="DELETE")
        if response:
            return response
        else:
            raise ValueError(response)

    def _query(self, url, method="GET", data=None, params=None, access_token=True, is_json=True):
        headers = {"content-type": "application/json" if is_json else "application/x-www-form-urlencoded"}
        if access_token:
            global_preferences = global_preferences_registry.manager()
            headers["Authorization"] = f'Bearer {global_preferences["wbintegrator_office365__access_token"]}'
        if method == "POST":
            response = requests.post(url, data=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, data=data, headers=headers)
        else:
            response = requests.get(url, headers=headers, params=params)
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            new_token = self._get_access_token()
            if new_token != global_preferences["wbintegrator_office365__access_token"]:
                global_preferences["wbintegrator_office365__access_token"] = new_token
                return self._query(
                    url, method=method, data=data, params=params, access_token=access_token, is_json=is_json
                )
        else:
            return response
