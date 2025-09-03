import uuid
from otrs_somconnexio.otrs_models.configurations.changes.change_email import ChangeEmailPersonalConfiguration
from otrs_somconnexio.otrs_models.ticket_types.base_customer_ticket import BaseCustomerTicket


class ChangePersonalEmailTicket(BaseCustomerTicket):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(ChangePersonalEmailTicket, self).__init__(
            username, customer_code, fields_dict, override_ticket_ids, fallback_path
        )
        self.configuration = ChangeEmailPersonalConfiguration

    def _get_queue_id(self):
        return self.configuration.queue_id

    def _get_subject(self):
        return self.configuration.subject

    def _get_dynamic_fields(self):
        return {
            "flagPartner": True,
            "IDOV": str(uuid.uuid4()),
            "nouEmail": self.fields["email"],
        }
