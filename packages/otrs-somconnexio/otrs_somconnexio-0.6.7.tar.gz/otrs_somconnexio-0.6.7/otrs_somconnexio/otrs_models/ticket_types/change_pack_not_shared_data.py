from otrs_somconnexio.otrs_models.configurations.changes.change_pack import (
    ChangePackNotSharedDataTicketConfiguration,
)
from .base_customer_ticket import BaseCustomerTicket


class ChangePackNotSharedDataTicket(BaseCustomerTicket):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(ChangePackNotSharedDataTicket, self).__init__(
            username, customer_code, fields_dict, override_ticket_ids, fallback_path
        )
        self.configuration = ChangePackNotSharedDataTicketConfiguration()

    def _get_queue_id(self):
        return self.configuration.queue_id

    def _get_subject(self):
        return self.configuration.subject

    def _get_service(self):
        return self.configuration.service

    def _get_dynamic_fields(self):
        return {
            "refOdooContract": ";".join(self.fields["selected_subscriptions"]),
            "fibraSenseFix": self._transform_boolean_df(
                self.fields["fiber_without_landline"]
            ),
        }
