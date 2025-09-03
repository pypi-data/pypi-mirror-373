from otrs_somconnexio.otrs_models.configurations.changes.add_data import (
    AddDataTicketConfiguration,
)

from otrs_somconnexio.otrs_models.ticket_types.base_customer_ticket import (
    BaseCustomerTicket,
)


class AddDataTicket(BaseCustomerTicket):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(AddDataTicket, self).__init__(
            username, customer_code, fields_dict, override_ticket_ids, fallback_path
        )
        self.configuration = AddDataTicketConfiguration()

    def _get_subject(self):
        return self.configuration.subject

    def _get_queue_id(self):
        return self.configuration.queue_id

    def _get_dynamic_fields(self):
        return {
            "liniaMobil": self.fields["phone_number"],
            "productAbonamentDadesAddicionals": self.fields["new_product_code"],
            "correuElectronic": self.fields["subscription_email"],
            "idioma": self.fields["language"],
        }
