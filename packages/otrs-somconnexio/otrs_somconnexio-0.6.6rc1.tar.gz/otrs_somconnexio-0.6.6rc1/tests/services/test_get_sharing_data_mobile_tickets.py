import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.configurations.provision.mobile_ticket import (
    MobileTicketPlatformIntroducedConfiguration as PIConf,
    MobileTicketActivationScheduledConfiguration as ASConf,
)
from otrs_somconnexio.services.get_sharing_data_mobile_tickets import (
    GetSharingDataMobileTickets,
)


@patch(
    "otrs_somconnexio.services.get_sharing_data_mobile_tickets.OTRSClient",
    return_value=Mock(
        spec=[
            "get_linked_tickets",
        ]
    ),
)
class TestGetSharingDataMobileTickets(unittest.TestCase):
    def setUp(self):
        self.ticket_id = 1
        self.ready_ticket = Mock(queue_id=ASConf.queue_id, state="new")
        self.provisioned_ticket = Mock(
            queue_id=PIConf.queue_id,
            state="new",
            shared_bond_id="id1",
        )

    def test_no_linked_tickets(self, MockOTRSClient):
        MockOTRSClient.return_value.get_linked_tickets.return_value = []

        result = GetSharingDataMobileTickets(self.ticket_id).run()

        self.assertEqual(result, {})

    def test_only_ready_mobile_tickets(self, MockOTRSClient):
        MockOTRSClient.return_value.get_linked_tickets.return_value = [
            self.ready_ticket
        ]

        result = GetSharingDataMobileTickets(self.ticket_id).run()

        self.assertEqual(len(result["ready_mobile_tickets"]), 1)
        self.assertEqual(len(result["unready_mobile_tickets"]), 0)

    def test_ready_and_unready_mobile_tickets(self, MockOTRSClient):
        unready_ticket = Mock(queue_id="other_queue", state="open")
        MockOTRSClient.return_value.get_linked_tickets.return_value = [
            self.ready_ticket,
            unready_ticket,
        ]

        result = GetSharingDataMobileTickets(self.ticket_id).run()

        self.assertEqual(len(result["ready_mobile_tickets"]), 1)
        self.assertEqual(len(result["unready_mobile_tickets"]), 1)

    def test_single_shared_bond_id(self, MockOTRSClient):
        MockOTRSClient.return_value.get_linked_tickets.return_value = [
            self.provisioned_ticket,
            self.provisioned_ticket,
        ]

        result = GetSharingDataMobileTickets(self.ticket_id).run()

        self.assertEqual(result["shared_bond_id"], ["id1"])

    def test_multiple_shared_bond_ids(self, MockOTRSClient):
        provisioned_ticket_2 = Mock(
            queue_id=PIConf.queue_id,
            state="new",
            shared_bond_id="id2",
        )
        MockOTRSClient.return_value.get_linked_tickets.return_value = [
            self.provisioned_ticket,
            provisioned_ticket_2,
        ]

        result = GetSharingDataMobileTickets(self.ticket_id).run()

        self.assertIn("id1", result["shared_bond_id"])
        self.assertIn("id2", result["shared_bond_id"])
        self.assertEqual(len(result["shared_bond_id"]), 2)

    def test_extracted_ticket_data(self, MockOTRSClient):
        ticket = Mock(
            id=1,
            number="T123",
            service_type="mobile",
            msisdn="123456789",
            product_code="P001",
            international_minutes=100,
            fiber_contract_code="F001",
            icc="ICC123",
            donor_icc="DICC123",
            previous_provider="ProviderX",
            previous_owner_docid="DOC123",
            previous_owner_name="John",
            previous_owner_surname="Doe",
            activation_date="2023-01-01",
            queue_id=ASConf.queue_id,
            state="new",
        )
        expected_data = {
            "ticket_id": 1,
            "ticket_number": "T123",
            "mobile_service_type": "mobile",
            "phone_number": "123456789",
            "product_code": "P001",
            "international_minutes": 100,
            "fiber_contract_code": "F001",
            "ICC_SC": "ICC123",
            "donor_ICC": "DICC123",
            "donor_operator": "ProviderX",
            "docid": "DOC123",
            "name": "John",
            "surname": "Doe",
            "activation_date": "2023-01-01",
        }
        MockOTRSClient.return_value.get_linked_tickets.return_value = [ticket]

        result = GetSharingDataMobileTickets(self.ticket_id).run()

        self.assertEqual(len(result["ready_mobile_tickets"]), 1)
        self.assertEqual(result["ready_mobile_tickets"], [expected_data])
