from otrs_somconnexio.client import OTRSClient
from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket import (
    ChangeTariffMobilePackTicket,
)


class ChangeTariffTicketMobilePack:
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        # TODO: Can we remove this field?
        fallback_path="/tmp/tickets/",
    ):
        self.username = username
        self.customer_code = customer_code
        self.fields = fields_dict
        self.override_ticket_ids = override_ticket_ids
        self.TicketClass = ChangeTariffMobilePackTicket

    def create(self):
        fields = self.fields
        contracts = fields.pop("contracts")
        otrs_client = OTRSClient()

        fields_creator = fields.copy()
        fields_creator.update({"pack_creator": True})
        ticket_creator = self._create_ticket(
            fields_creator, contracts.pop(0), self.override_ticket_ids
        )
        for contract in contracts:
            ticket = self._create_ticket(fields, contract, self.override_ticket_ids)
            otrs_client.link_tickets(
                ticket_creator.id, ticket.id, link_type="ParentChild"
            )

    def _create_ticket(self, fields, contract, override_ticket_ids):
        fields["phone_number"] = contract["phone_number"]
        fields["current_product_code"] = contract["current_product_code"]
        fields["subscription_email"] = contract["subscription_email"]

        return self.TicketClass(
            self.username, self.customer_code, fields, override_ticket_ids
        ).create()

    def update(self, ticket_id, article=None, dynamic_fields=None, state=None):
        self.TicketClass(self.username, self.customer_code, {}).update(
            ticket_id, article, dynamic_fields, state
        )
