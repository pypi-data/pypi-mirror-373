# coding: utf-8
from pyotrs.lib import DynamicField

from .update_ticket_DF import UpdateTicketDF


class SetFiberContractCodeMobileTicket(UpdateTicketDF):
    """
    Set DF OdooContractRefRelacionat to OTRS mobile tickets.
    """

    def __init__(self, ticket_number, fiber_contract_code):
        self.fiber_contract_code = fiber_contract_code
        super().__init__(ticket_number)

    def _prepare_dynamic_fields(self):
        return [
            DynamicField(
                name="OdooContractRefRelacionat", value=self.fiber_contract_code
            )
        ]
