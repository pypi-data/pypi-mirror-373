from otrs_somconnexio.otrs_models.configurations.changes.change_iban import (
    ChangeIbanTicketConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.base_change_ticket import (
    BaseChangeTicket,
)


class ChangeIbanTicket(BaseChangeTicket):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(ChangeIbanTicket, self).__init__(
            username, customer_code, fields_dict, override_ticket_ids, fallback_path
        )
        self.configuration = ChangeIbanTicketConfiguration()

    def _get_activity_id(self):
        return self.configuration.activity_id

    def _get_process_id(self):
        return self.configuration.process_id

    def _get_queue_id(self):
        return self.configuration.queue_id

    def _get_subject(self):
        return self.configuration.subject

    def _attribute_to_change(self):
        return "IBAN"

    def _get_attribute_dynamic_field_name(self):
        return "nouIBAN"
