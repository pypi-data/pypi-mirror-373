from typing import Iterable, cast

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import CustomReportCriteria, CustomReport
from sapiopylib.rest.pojo.webhook.WebhookDirective import HomePageDirective, FormDirective, TableDirective, \
    CustomReportDirective, ElnExperimentDirective, ExperimentEntryDirective

from sapiopycommons.general.aliases import SapioRecord, AliasUtil, ExperimentIdentifier, ExperimentEntryIdentifier, \
    UserIdentifier
from sapiopycommons.general.custom_report_util import CustomReportUtil


# FR-47392: Create a DirectiveUtil class to simplify the creation of directives.
class DirectiveUtil:
    """
    DirectiveUtil is a class for creating webhook directives. The utility functions reduce the provided variables
    down to the exact type that the directives require, removing the need for the caller to handle the conversion.
    """
    user: SapioUser

    def __init__(self, context: UserIdentifier):
        """
        :param context: The current webhook context or a user object to send requests from.
        """
        self.user = AliasUtil.to_sapio_user(context)

    @staticmethod
    def homepage() -> HomePageDirective:
        """
        :return: A directive that sends the user back to their home page.
        """
        return HomePageDirective()

    @staticmethod
    def record_form(record: SapioRecord) -> FormDirective:
        """
        :param record: A record in the system.
        :return: A directive that sends the user to a specific data record form.
        """
        return FormDirective(AliasUtil.to_data_record(record))

    @staticmethod
    def record_table(records: Iterable[SapioRecord]) -> TableDirective:
        """
        :param records: A list of records in the system.
        :return: A directive that sends the user to a table of data records.
        """
        return TableDirective(AliasUtil.to_data_records(records))

    @staticmethod
    def record_adaptive(records: Iterable[SapioRecord]) -> TableDirective | FormDirective:
        """
        :param records: A list of records in the system.
        :return: A directive that sends the user to a table of data records if there are multiple records,
            or a directive that sends the user to a specific data record form if there is only one record.
        """
        records: list[SapioRecord] = list(records)
        if len(records) == 1:
            return DirectiveUtil.record_form(records[0])
        return DirectiveUtil.record_table(records)

    def custom_report(self, report: CustomReport | CustomReportCriteria | str) -> CustomReportDirective:
        """
        :param report: A custom report, the criteria for a custom report, or the name of a system report.
        :return: A directive that sends the user to the results of the provided custom report.
        """
        if isinstance(report, str):
            report: CustomReport = CustomReportUtil.get_system_report_criteria(self.user, report)
        return CustomReportDirective(cast(CustomReport, report))

    @staticmethod
    def eln_experiment(experiment: ExperimentIdentifier) -> ElnExperimentDirective:
        """
        :param experiment: An identifier for an experiment.
        :return: A directive that sends the user to the ELN experiment.
        """
        return ElnExperimentDirective(AliasUtil.to_notebook_id(experiment))

    @staticmethod
    def eln_entry(experiment: ExperimentIdentifier, entry: ExperimentEntryIdentifier) -> ExperimentEntryDirective:
        """
        :param experiment: An identifier for an experiment.
        :param entry: An identifier for an entry in the experiment.
        :return: A directive that sends the user to the provided experiment entry within its ELN experiment.
        """
        return ExperimentEntryDirective(AliasUtil.to_notebook_id(experiment), AliasUtil.to_entry_id(entry))
