from openapi.api.plans_api import PlansApi
from vayu_sdk.clients.vayu_client import VayuClient

from openapi.models.get_plan_response_plan import GetPlanResponsePlan
from openapi.models.list_plans_response import ListPlansResponse
from openapi.models.get_plan_response import GetPlanResponse
from openapi.models.delete_plan_response import DeletePlanResponse

Plan = GetPlanResponsePlan

class PlansAPI:
    __client: PlansApi = None

    def __init__(self, vayu_client: VayuClient):
        vayu_client.validate_logged_in()
        self.__client = PlansApi(vayu_client.client)

    def list(self, limit: int = None, cursor: int = None):
        return self.__client.list_plans(limit=limit, cursor=cursor)

    def get(self, id: str):
        get_plans_response = self.__client.get_plan(plan_id=id)

        return get_plans_response

    def delete(self, id: str):
        delete_plan_response = self.__client.delete_plan(plan_id=id)

        return delete_plan_response

