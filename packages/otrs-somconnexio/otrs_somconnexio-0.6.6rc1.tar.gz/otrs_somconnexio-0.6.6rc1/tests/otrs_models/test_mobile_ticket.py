# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.mobile_ticket import MobileTicket
from otrs_somconnexio.otrs_models.configurations.provision.mobile_ticket import (
    MobileTicketConfiguration,
)


class MobileTicketTestCase(unittest.TestCase):
    @patch("otrs_somconnexio.otrs_models.provision_ticket.Ticket")
    def test_build_ticket(self, MockTicket):
        mobile_data = Mock(spec=["order_id", "technology"])
        mobile_data.order_id = 123

        customer_data = Mock(spec=["id"])

        expected_ticket_arguments = {
            "Title": "Ticket#{} - Només mòbil".format(mobile_data.order_id),
            "Type": MobileTicketConfiguration.type,
            "QueueID": MobileTicketConfiguration.queue_id,
            "State": MobileTicketConfiguration.state,
            "SLA": "No pendent resposta",
            "Service": "Mòbil",
            "Priority": MobileTicketConfiguration.priority,
            "CustomerUser": customer_data.id,
            "CustomerID": customer_data.id,
        }

        MobileTicket(mobile_data, customer_data)._build_ticket()

        MockTicket.assert_called_with(expected_ticket_arguments)

    @patch("otrs_somconnexio.otrs_models.provision_ticket.ProvisionArticle")
    def test_build_article(self, MockProvisionArticle):
        mobile_data = Mock(spec=["order_id", "notes", "technology"])
        mobile_data.order_id = 123
        mobile_data.notes = "Hola mundo"

        customer_data = Mock(spec=["order_id"])

        mock_mobile_article = MockProvisionArticle.return_value

        MobileTicket(mobile_data, customer_data)._build_article()

        MockProvisionArticle.assert_called_with(
            mobile_data.technology, mobile_data.order_id, "mobile", mobile_data.notes
        )
        mock_mobile_article.call.assert_called_once()

    @patch("otrs_somconnexio.otrs_models.mobile_ticket.MobileDynamicFields")
    def test_build_dynamic_fields(self, MockMobileDynamicFields):
        mobile_data = Mock(spec=[])
        customer_data = Mock(spec=[])

        mock_mobile_dynamic_fields = MockMobileDynamicFields.return_value

        MobileTicket(mobile_data, customer_data)._build_dynamic_fields()

        MockMobileDynamicFields.assert_called_with(
            mobile_data,
            customer_data,
            MobileTicketConfiguration.process_id,
            MobileTicketConfiguration.activity_id,
        )
        mock_mobile_dynamic_fields.all.assert_called_once()

    @patch("otrs_somconnexio.otrs_models.provision_ticket.OTRSClient")
    def test_create(self, MockOTRSClient):
        mobile_data = Mock(
            spec=[
                "order_id",
                "iban",
                "email",
                "contact_phone",
                "phone_number",
                "sc_icc",
                "icc",
                "type",
                "previous_provider",
                "previous_owner_vat",
                "previous_owner_name",
                "previous_owner_surname",
                "product",
                "notes",
                "activation_notes",
                "has_sim",
                "sim_delivery_tracking_code",
                "type",
                "delivery_street",
                "delivery_city",
                "delivery_zip_code",
                "delivery_state",
                "technology",
                "sales_team",
                "fiber_linked",
                "shared_bond_id",
            ]
        )
        mobile_data.order_id = 4321
        mobile_data.type = "new"

        customer_data = Mock(
            spec=[
                "id",
                "first_name",
                "name",
                "vat_number",
                "street",
                "city",
                "zip",
                "subdivision",
                "has_active_contracts",
                "language",
            ]
        )
        customer_data.id = 1234

        mock_otrs_client = Mock(spec=["create_otrs_process_ticket"])
        mock_otrs_client.create_otrs_process_ticket.return_value = Mock(
            MobileTicket, autospec=True
        )
        mock_otrs_client.create_otrs_process_ticket.return_value.id = 123
        mock_otrs_client.create_otrs_process_ticket.return_value.number = "#123"
        MockOTRSClient.return_value = mock_otrs_client

        ticket = MobileTicket(mobile_data, customer_data)
        ticket.create()

        mock_otrs_client.create_otrs_process_ticket.assert_called_once()

        self.assertEqual(ticket.id, 123)
        self.assertEqual(ticket.number, "#123")
