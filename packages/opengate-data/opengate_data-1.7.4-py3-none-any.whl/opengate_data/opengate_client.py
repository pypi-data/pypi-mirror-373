import os
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from .searching.filter import FilterBuilder
from .searching.select import SelectBuilder
from .searching.builder.entities_search import EntitiesSearchBuilder
from .searching.builder.operations_search import OperationsSearchBuilder
from .searching.builder.datapoints_search import DataPointsSearchBuilder
from .searching.builder.datasets_search import DatasetsSearchBuilder
from .searching.builder.timeseries_search import TimeseriesSearchBuilder
from .searching.builder.rules_search import RulesSearchBuilder
from .ai_models.ai_models import AIModelsBuilder
from .ai_pipelines.ai_pipelines import AIPipelinesBuilder
from .ai_transformers.ai_transformers import AITransformersBuilder
from .rules.rules import RulesBuilder
from .collection.iot_collection import IotCollectionBuilder
from .collection.iot_bulk_collection import IotBulkCollectionBuilder
from .collection.pandas_iot_collection import PandasIotCollectionBuilder
from .provision.bulk.provision_bulk import ProvisionBulkBuilder
from .provision.processor.provision_processor import ProvisionProcessorBuilder
from .utils.utils import validate_type, send_request
from .provision.asset.provision_asset import ProvisionAssetBuilder
from .provision.devices.provision_device import ProvisionDeviceBuilder


class OpenGateClient:
    """ Class representing the OpenGateClient """

    def __init__(self, url: str | None = None, user: str | None = None, password: str | None = None,
                 api_key: str | None = None) -> None:
        self.token_jwt: str = os.getenv("TOKEN_JWT")
        self.url: str | None = url
        self.user: str | None = user
        self.password: str | None = password
        self.api_key: str | None = api_key
        self.headers: dict[str, str] = {}
        self.client: OpenGateClient = self
        self.entity_type: str | None = None
        disable_warnings(InsecureRequestWarning)

        if self.user and self.password:
            validate_type(user, str, "User")
            validate_type(password, str, "Password")

            data_user = {
                'email': self.user,
                'password': self.password
            }
            if self.url:
                validate_type(url, str, "Url")
                login_url = self.url + '/north/v80/provision/users/login'
            else:
                login_url = "https://logger:4445/v80/provision/users/login"

            request = send_request(
                method='post', url=login_url, json_payload=data_user)
            request.raise_for_status()
            response_json = request.json()
            if 'user' in response_json:
                self.headers.update({
                    'Authorization': f'Bearer {response_json["user"]["jwt"]}',
                })
            else:
                raise ValueError('Empty response received')

        elif self.api_key:
            validate_type(self.api_key, str, "Api-Key")
            self.headers.update({
                'X-ApiKey': self.api_key
            })

        elif self.token_jwt:
            self.headers.update({
                'Authorization': f'Bearer {self.token_jwt}',
            })
        else:
            raise ValueError(
                'You must provide either a user and password or an API key or JWT Token, either as a parameter or in the environment variable API_KEY, or TOKEN_JWT')

    def new_entities_search_builder(self) -> EntitiesSearchBuilder:
        """ Represents the search builder of entities """
        return EntitiesSearchBuilder(self)

    def new_operations_search_builder(self) -> OperationsSearchBuilder:
        """ Represents the search builder of operations """
        return OperationsSearchBuilder(self)

    def new_datapoints_search_builder(self) -> DataPointsSearchBuilder:
        """ Represents the search builder of datapoints """
        return DataPointsSearchBuilder(self)

    def new_data_sets_search_builder(self) -> DatasetsSearchBuilder:
        """ Represents the search builder of datasets """
        return DatasetsSearchBuilder(self)

    def new_timeseries_search_builder(self) -> TimeseriesSearchBuilder:
        """ Represents the builder of timeseries """
        return TimeseriesSearchBuilder(self)

    def new_provision_processor_builder(self) -> ProvisionProcessorBuilder:
        """ Represents the builder of provision processors """
        return ProvisionProcessorBuilder(self)

    def new_ai_models_builder(self) -> AIModelsBuilder:
        """ Represents the builder of artificial intelligence models """
        return AIModelsBuilder(self)

    def new_ai_pipelines_builder(self) -> AIPipelinesBuilder:
        """ Represents the builder of artificial intelligence models """
        return AIPipelinesBuilder(self)

    def new_ai_transformers_builder(self) -> AITransformersBuilder:
        """ Represents the builder of artificial intelligence models """
        return AITransformersBuilder(self)

    def new_rules_builder(self) -> RulesBuilder:
        """ Represents the builder rules """
        return RulesBuilder(self)

    def new_rules_search_builder(self) -> RulesSearchBuilder:
        """ Represents the builder rules """
        return RulesSearchBuilder(self)

    def new_iot_collection_builder(self) -> IotCollectionBuilder:
        """ Represents the builder iot collection builder """
        return IotCollectionBuilder(self)

    def new_iot_bulk_collection_builder(self) -> IotBulkCollectionBuilder:
        """ Represents the builder iot bulk collection builder """
        return IotBulkCollectionBuilder(self)

    def new_provision_bulk_builder(self) -> ProvisionBulkBuilder:
        """ Represents the builder iot bulk collection builder """
        return ProvisionBulkBuilder(self)

    def new_provision_asset_builder(self) -> ProvisionAssetBuilder:
        """ Represents the builder provision asset builder """
        return ProvisionAssetBuilder(self)

    def new_provision_device_builder(self) -> ProvisionDeviceBuilder:
        """ Represents the builder provision device builder """
        return ProvisionDeviceBuilder(self)

    def new_pandas_iot_collection_builder(self) -> PandasIotCollectionBuilder:
        """ Represents the builder pandas iot bulk collection builder """
        return PandasIotCollectionBuilder(self)

    @staticmethod
    def new_filter_builder() -> FilterBuilder:
        """ Represents the builder of filter """
        return FilterBuilder()

    @staticmethod
    def new_select_builder() -> SelectBuilder:
        """ Represents the builder of select """
        return SelectBuilder()
