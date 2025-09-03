from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket_mobile_pack import (
    ChangeTariffTicketMobilePack,
)
from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket import (
    ChangeTariffSharedBondTicket,
)


class ChangeTariffTicketSharedBond(ChangeTariffTicketMobilePack):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        # TODO: Can we remove this field?
        fallback_path="/tmp/tickets/",
    ):
        super(ChangeTariffTicketSharedBond, self).__init__(
            username, customer_code, fields_dict, override_ticket_ids, fallback_path
        )
        self.TicketClass = ChangeTariffSharedBondTicket
