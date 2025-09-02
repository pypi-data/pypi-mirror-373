from functools import singledispatch
from typing import List
from openapi.api.customers_api import CustomersApi
from openapi.models.contact import Contact
from vayu_sdk.clients.vayu_client import VayuClient
from openapi.models.create_customer_request import CreateCustomerRequest
from openapi.models.update_customer_request import UpdateCustomerRequest

from openapi.models.create_customer_response_customer import (
    CreateCustomerResponseCustomer,
)
from openapi.models.list_customers_response import ListCustomersResponse
from openapi.models.get_customer_response import GetCustomerResponse
from openapi.models.create_customer_response import CreateCustomerResponse
from openapi.models.update_customer_response import UpdateCustomerResponse
from openapi.models.delete_customer_response import DeleteCustomerResponse
from openapi.models.address import Address


Customer = CreateCustomerResponseCustomer


class CustomersAPI:
    __client: CustomersApi = None

    def __init__(self, vayu_client: VayuClient):
        vayu_client.validate_logged_in()
        self.__client = CustomersApi(vayu_client.client)

    def list(self, cursor: str = None, limit: int = None):
        return self.__client.list_customers(limit=limit, cursor=cursor)

    def get(self, id: str):
        response = self.__client.get_customer(customer_id=id)

        return response
    
    def getByExternalId(self, external_id: str):
        response = self.__client.get_customer_by_external_id(external_id=external_id)

        return response

    def create(
        self, name: str, external_id: str, aliases: List[str] = [], address: Address = None, contacts: List[Contact] = None
    ):
        request = CreateCustomerRequest(
            name=name, externalId=external_id, aliases=aliases, address=address, contacts=contacts
        )
        response = self.__client.create_customer(create_customer_request=request)
        return response

    def update(self, id: str, name: str = None, external_id: str = None, aliases: List[str] = None, address: Address = None, contacts: List[Contact] = None):
        request = UpdateCustomerRequest(name=name, externalId=external_id, address=address, contacts=contacts, aliases=aliases)
        response = self.__client.update_customer(customer_id=id, update_customer_request=request)

        return response

    def delete(self, id: str):
        response = self.__client.delete_customer(customer_id=id)

        return response
