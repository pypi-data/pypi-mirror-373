# coding: utf-8
from pyotrs.lib import DynamicField

from otrs_somconnexio.services.update_ticket_DF import UpdateTicketDF


class UnblockMobilePackTicket(UpdateTicketDF):
    """
    Unblock the mobile pack tickets.

    Once the fiber provisioning is closed, we can start with the mobile provisioning to complete
    the pack products.
    Unblock is to change the DynamicField_recuperarProvisio to 1
    """

    def __init__(self, ticket_number, activation_date, introduced_date):
        self.activation_date = activation_date
        self.introduced_date = introduced_date
        super().__init__(ticket_number)

    def _prepare_dynamic_fields(self):
        dynamic_fields = [
            DynamicField(name="recuperarProvisio", value=1),
            DynamicField(name="enviarNotificacio", value=0),
        ]
        if bool(self.ticket.dynamic_field_get("SIMrebuda").value):
            dynamic_fields.append(
                DynamicField(
                    name="dataActivacioLiniaMobil", value=self.activation_date
                ),
            )
            dynamic_fields.append(
                DynamicField(name="dataIntroPlataforma", value=self.introduced_date),
            )
        return dynamic_fields

    def run(self):
        self._get_ticket()
        if (
            self.ticket.dynamic_field_get("dataIntroPlataforma").value
            and self.ticket.dynamic_field_get("dataActivacioLiniaMobil").value
        ):
            return
        self.otrs_client.update_ticket(
            self.ticket.tid,
            article=None,
            dynamic_fields=self._prepare_dynamic_fields(),
        )
