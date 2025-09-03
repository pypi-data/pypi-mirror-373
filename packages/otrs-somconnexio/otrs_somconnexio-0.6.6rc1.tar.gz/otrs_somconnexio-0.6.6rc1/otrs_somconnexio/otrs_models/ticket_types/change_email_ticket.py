from otrs_somconnexio.otrs_models.configurations.changes.change_email import (
    ChangeEmailContractsConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.base_change_ticket import (
    BaseChangeTicket,
)


class ChangeEmailTicket(BaseChangeTicket):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(ChangeEmailTicket, self).__init__(
            username, customer_code, fields_dict, override_ticket_ids, fallback_path
        )
        self.configuration = ChangeEmailContractsConfiguration

    def _get_queue_id(self):
        return self.configuration.queue_id

    def _get_subject(self):
        return self.configuration.subject

    def _attribute_to_change(self):
        return "email"

    def _get_attribute_dynamic_field_name(self):
        return "nouEmail"

    def _get_dynamic_fields(self):
        result = super()._get_dynamic_fields()

        result.update({"flagContracts": True})

        return result
