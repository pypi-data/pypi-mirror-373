from openapi.api.meters_api import MetersApi
from vayu_sdk.clients.vayu_client import VayuClient
from openapi.models.update_meter_request import UpdateMeterRequest

from openapi.models.aggregation_operator import AggregationOperator
from openapi.models.aggregation_method import AggregationMethod
from openapi.models.filter import Filter
from openapi.models.condition import Condition
from openapi.models.criterion import Criterion
from openapi.models.criterion_operator import CriterionOperator

from openapi.models.meter import Meter
from openapi.models.list_meters_response import ListMetersResponse
from openapi.models.get_meter_response import GetMeterResponse
from openapi.models.update_meter_response import UpdateMeterResponse
from openapi.models.delete_meter_response import DeleteMeterResponse


class MetersAPI:
    __client: MetersApi = None

    def __init__(self, vayu_client: VayuClient):
        vayu_client.validate_logged_in()
        self.__client = MetersApi(vayu_client.client)

    def list(self, limit: int = None, cursor: int = None):
        return self.__client.list_meters(limit=limit, cursor=cursor)

    def get(self, id: str):
        response = self.__client.get_meter(meter_id=id)

        return response

    def update(
        self,
        id: str,
        name: str = None,
        event_name: str = None,
        aggregation_method: AggregationMethod = None,
        filter: Filter = None,
    ):
        request = UpdateMeterRequest(
            name=name,
            eventName=event_name,
            aggregationMethod=aggregation_method,
            filter=filter,
        )

        response = self.__client.update_meter(meter_id=id, update_meter_request=request)

        return response

    def delete(self, id: str):
        response = self.__client.delete_meter(meter_id=id)

        return response
