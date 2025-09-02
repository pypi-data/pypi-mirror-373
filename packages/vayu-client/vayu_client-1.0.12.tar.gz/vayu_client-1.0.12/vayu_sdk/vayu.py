from .clients import VayuClient
from .apis import * 

class Vayu:
    __api_key: str = None
    __host: str = None
    __client: VayuClient = None

    def __init__(self, api_key: str, host: str = None):
        self.__client = None
        self.__host = host
        self.__api_key = api_key

    @property
    def contracts(self) -> ContractsAPI:
        return ContractsAPI(self.__client)

    @property
    def customers(self) -> CustomersAPI:
        return CustomersAPI(self.__client)

    @property
    def events(self) -> EventsAPI:
        return EventsAPI(self.__client)

    @property
    def invoices(self) -> InvoicesAPI:
        return InvoicesAPI(self.__client)

    @property
    def meters(self) -> MetersAPI:
        return MetersAPI(self.__client)

    @property
    def plans(self) -> PlansAPI:
        return PlansAPI(self.__client)
    
    @property
    def webhooks(self) -> WebhooksAPI:
        return WebhooksAPI(self.__client)
    
    def login(self):
        self.__client = VayuClient(self.__api_key, self.__host)
        self.__client.login()
