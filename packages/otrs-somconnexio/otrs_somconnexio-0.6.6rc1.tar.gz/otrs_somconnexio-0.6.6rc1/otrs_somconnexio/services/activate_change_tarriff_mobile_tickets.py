# coding: utf-8
from pyotrs.lib import DynamicField

from .update_ticket_DF import UpdateTicketDF


class ActivateChangeTariffMobileTickets(UpdateTicketDF):
    """
    Set DF enviaraMM to OTRS mobile tickets.
    """

    def _prepare_dynamic_fields(self):
        return [DynamicField(name="enviatMMOV", value=1)]
