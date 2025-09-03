from ..otrs_models.configurations.provision.mobile_ticket import (
    MobileTicketPlatformIntroducedConfiguration as PIConf,
    MobileTicketActivationScheduledConfiguration as ASConf,
)
from ..client import OTRSClient


class GetSharingDataMobileTickets:
    def __init__(self, ticket_id):
        self.ticket_id = ticket_id
        self.otrs_client = OTRSClient()

    def run(self):
        linked_tickets = [
            t
            for t in self.otrs_client.get_linked_tickets(self.ticket_id, "Normal")
            if t.state in ["new", "open"]
        ]

        if not linked_tickets:
            return {}

        ticket_dict = {"provisioned": [], "ready": [], "unready": []}

        for t in linked_tickets:
            if t.queue_id == PIConf.queue_id:
                ticket_dict["provisioned"].append(t)
            elif t.queue_id == ASConf.queue_id:
                ticket_dict["ready"].append(t)
            else:
                ticket_dict["unready"].append(t)

        return {
            "shared_bond_id": self._get_shared_bond_id(ticket_dict["provisioned"]),
            "ready_mobile_tickets": [
                self._extract_ticket_data(ticket) for ticket in ticket_dict["ready"]
            ],
            "unready_mobile_tickets": [
                self._extract_ticket_data(ticket) for ticket in ticket_dict["unready"]
            ],
        }

    def _get_shared_bond_id(self, provisioned_tickets):
        shared_bond_ids = set(
            t.shared_bond_id for t in provisioned_tickets if t.shared_bond_id
        )
        return list(shared_bond_ids)

    def _extract_ticket_data(self, ticket):
        return {
            "ticket_id": ticket.id,
            "ticket_number": ticket.number,
            "mobile_service_type": ticket.service_type,
            "phone_number": ticket.msisdn,
            "product_code": ticket.product_code,
            "international_minutes": ticket.international_minutes,
            "fiber_contract_code": ticket.fiber_contract_code,
            "ICC_SC": ticket.icc,
            "donor_ICC": ticket.donor_icc,
            "donor_operator": ticket.previous_provider,
            "docid": ticket.previous_owner_docid,
            "name": ticket.previous_owner_name,
            "surname": ticket.previous_owner_surname,
            "activation_date": ticket.activation_date,
        }
