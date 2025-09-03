# coding: utf-8
from pyotrs.lib import DynamicField

from otrs_somconnexio.otrs_models.abstract_article import AbstractArticle
from otrs_somconnexio.services.update_ticket_DF import UpdateTicketDF


class SIMReturnedArticle(AbstractArticle):
    def __init__(self):
        self.subject = "PROCÉS DE DEVOLUCIÓ DE LA SIM"
        self.body = "PROCÉS DE DEVOLUCIÓ DE LA SIM"


class SetSIMReturnedMobileTicket(UpdateTicketDF):
    """
    Empty referenciaCorreus DF to OTRS mobile tickets.
    """

    def __init__(
        self,
        ticket_number,
    ):
        super().__init__(ticket_number)
        self._get_ticket()

    def _prepare_dynamic_fields(self):
        return [
            DynamicField(name="referenciaCorreus", value=""),
            DynamicField(name="SIMrebuda", value=0),
        ]

    def run(self):
        super(SetSIMReturnedMobileTicket, self).run()
        self.otrs_client.update_ticket(
            self.ticket.tid,
            article=SIMReturnedArticle().call(),
        )
