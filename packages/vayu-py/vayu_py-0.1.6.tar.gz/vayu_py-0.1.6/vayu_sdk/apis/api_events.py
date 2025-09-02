from openapi.api.events_api import EventsApi
from vayu_sdk.clients.vayu_client import VayuClient
from openapi.models.send_events_request import SendEventsRequest
from typing import List
from datetime import datetime

from openapi.models.event import Event
from openapi.models.get_event_response import GetEventResponse
from openapi.models.delete_event_response import DeleteEventResponse
from openapi.models.query_events_response import QueryEventsResponse
from openapi.models.send_events_response import SendEventsResponse
from openapi.models.events_dry_run_response import EventsDryRunResponse


class EventsAPI:
    __client: EventsApi = None

    def __init__(self, vayu_client: VayuClient):
        vayu_client.validate_logged_in()
        self.__client = EventsApi(vayu_client.client)

    def get(self, ref: str):
        response = self.__client.get_event_by_ref_id(ref_id=ref)

        return response

    def delete(self, ref: str):
        response = self.__client.delete_event_by_ref_id(ref_id=ref)

        return response

    def query(
        self,
        start_time: datetime,
        end_time: datetime,
        event_name: str,
        cursor: str = None,
        limit: int = None,
    ):
        response = self.__client.query_events(
            start_time=start_time,
            end_time=end_time,
            event_name=event_name,
            cursor=cursor,
            limit=limit,
        )

        return response

    def send(self, events: List[Event]):
        request = SendEventsRequest(events=events)

        return self.__client.send_events(send_events_request=request)

    def dry_run(self, events: List[Event]):
        request = SendEventsRequest(events=events)

        return self.__client.send_events_dry_run(events_dry_run_request=request)

