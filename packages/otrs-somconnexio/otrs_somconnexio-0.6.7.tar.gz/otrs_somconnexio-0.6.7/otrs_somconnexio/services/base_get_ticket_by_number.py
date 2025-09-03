# coding: utf-8
from otrs_somconnexio.client import OTRSClient


class BaseGetTicketByNumber:
    """ """

    def __init__(self, ticket_number):
        self.ticket_number = ticket_number
        self.ticket = None
        self.otrs_client = None

    def _get_ticket(self):
        if not self.otrs_client:
            self.otrs_client = OTRSClient()
        if not self.ticket:
            self.ticket = self.otrs_client.get_ticket_by_number(
                self.ticket_number, dynamic_fields=True
            )

    def run(self):
        self._get_ticket()
