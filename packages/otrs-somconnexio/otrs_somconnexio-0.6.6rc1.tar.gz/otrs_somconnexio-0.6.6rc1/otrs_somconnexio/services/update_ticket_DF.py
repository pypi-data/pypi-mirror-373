# coding: utf-8
from otrs_somconnexio.services.base_get_ticket_by_number import BaseGetTicketByNumber


class UpdateTicketDF(BaseGetTicketByNumber):
    """
    Abstract service class to update a given OTRS ticket DF's.

    Class method '_prepare_dynamic_fields' needs to be implemented in child classes
    """

    def run(self):
        super().run()
        self.otrs_client.update_ticket(
            self.ticket.tid,
            article=None,
            dynamic_fields=self._prepare_dynamic_fields(),
        )
