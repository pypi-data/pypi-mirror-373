from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext

from sapiopycommons.general.aliases import RecordIdentifier, ExperimentIdentifier, AliasUtil, DataTypeIdentifier
from sapiopycommons.general.exceptions import SapioException


class SapioNavigationLinker:
    """
    Given a URL to a system's webservice API (example: https://company.exemplareln.com/webservice/api), construct
    URLs for navigation links to various locations in the system.
    """
    client_url: str
    webservice_url: str

    def __init__(self, url: str | SapioUser | SapioWebhookContext):
        """
        :param url: A user or context object that is being used to send requests to a Sapio system, or a URL to a
            system's webservice API.
        """
        if isinstance(url, SapioWebhookContext):
            url = url.user.url
        elif isinstance(url, SapioUser):
            url = url.url
        self.webservice_url = url.rstrip("/")
        self.client_url = url.rstrip("/").replace('webservice/api', 'veloxClient')

    def homepage(self) -> str:
        """
        :return: A URL for navigating to the system's homepage.
        """
        return self.client_url + "/#view=homepage"

    def data_record(self, record_identifier: RecordIdentifier, data_type_name: DataTypeIdentifier | None = None) -> str:
        """
        :param record_identifier: An object that can be used to identify a record in the system, be that a record ID,
            a data record, or a record model.
        :param data_type_name: If the provided record identifier is a record ID, then the data type name of the record
            must be provided in this parameter. Otherwise, this parameter is ignored.
        :return: A URL for navigating to the input record.
        """
        record_id: int = AliasUtil.to_record_id(record_identifier)
        if data_type_name:
            data_type_name = AliasUtil.to_data_type_name(data_type_name)
        if not isinstance(record_identifier, int):
            data_type_name = AliasUtil.to_data_type_name(record_identifier)
        if not data_type_name:
            raise SapioException("Unable to create a data record link without a data type name. "
                                 "Only a record ID was provided.")
        return self.client_url + f"/#dataType={data_type_name};recordId={record_id};view=dataRecord"

    def experiment(self, experiment: ExperimentIdentifier) -> str:
        """
        :param experiment: An object that can be used to identify an experiment in the system, be that an experiment
            object, experiment protocol, or a notebook ID.
        :return: A URL for navigating to the input experiment.
        """
        return self.client_url + f"/#notebookExperimentId={AliasUtil.to_notebook_id(experiment)};view=eln"
