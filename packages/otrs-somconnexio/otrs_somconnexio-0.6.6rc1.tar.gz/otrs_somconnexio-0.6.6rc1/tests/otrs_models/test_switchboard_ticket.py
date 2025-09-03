# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.switchboard_ticket import SwitchboardTicket
from otrs_somconnexio.otrs_models.configurations.provision.switchboard_ticket import (
    SwitchboardTicketConfiguration,
)


class SwitchboardTicketTestCase(unittest.TestCase):
    @patch("otrs_somconnexio.otrs_models.provision_ticket.Ticket")
    def test_build_ticket(self, MockTicket):
        service_data = Mock(spec=["order_id", "notes", "technology"])
        service_data.order_id = 123
        customer_data = Mock(spec=["id"])

        expected_ticket_arguments = {
            "Title": "Ticket#{} - Només Centraleta Virtual".format(
                service_data.order_id
            ),
            "Type": SwitchboardTicketConfiguration.type,
            "QueueID": SwitchboardTicketConfiguration.queue_id,
            "State": SwitchboardTicketConfiguration.state,
            "SLA": "No pendent resposta",
            "Service": "Centraleta Virtual",
            "Priority": SwitchboardTicketConfiguration.priority,
            "CustomerUser": customer_data.id,
            "CustomerID": customer_data.id,
        }

        SwitchboardTicket(service_data, customer_data)._build_ticket()
        MockTicket.assert_called_with(expected_ticket_arguments)

    @patch("otrs_somconnexio.otrs_models.provision_ticket.ProvisionArticle")
    def test_build_article(self, MockProvisionArticle):
        service_data = Mock(spec=["order_id", "notes", "technology"])
        service_data.order_id = 123
        service_data.notes = "Notes test"
        customer_data = Mock(spec=["order_id"])

        mock_article = MockProvisionArticle.return_value

        SwitchboardTicket(service_data, customer_data)._build_article()
        MockProvisionArticle.assert_called_with(
            service_data.technology,
            service_data.order_id,
            "switchboard",
            service_data.notes,
        )
        mock_article.call.assert_called_once()

    @patch("otrs_somconnexio.otrs_models.switchboard_ticket.SwitchboardDynamicFields")
    def test_build_dynamic_fields(self, MockSwitchboardDynamicFields):
        service_data = Mock()
        customer_data = Mock()
        mock_dyn_fields = MockSwitchboardDynamicFields.return_value

        SwitchboardTicket(service_data, customer_data)._build_dynamic_fields()
        MockSwitchboardDynamicFields.assert_called_with(
            service_data,
            customer_data,
            SwitchboardTicketConfiguration.process_id,
            SwitchboardTicketConfiguration.activity_id,
        )
        mock_dyn_fields.all.assert_called_once()

    @patch("otrs_somconnexio.otrs_models.provision_ticket.OTRSClient")
    def test_create(self, MockOTRSClient):
        service_data = Mock(
            spec=[
                "order_id",
                "iban",
                "email",
                "contact_phone",
                "product",
                "technology",
                "sales_team",
                "type",
                "landline",
                "mobile_phone_number",
                "icc",
                "has_sim",
                "extension",
                "agent_name",
                "agent_email",
                "previous_owner_vat",
                "previous_owner_name",
                "previous_owner_surname",
                "shipment_address",
                "shipment_city",
                "shipment_zip",
                "shipment_subdivision",
                "additional_products",
                "activation_notes",
                "notes",
            ]
        )
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

        mock_otrs_client = Mock(spec=["create_otrs_process_ticket"])
        mock_otrs_client.create_otrs_process_ticket.return_value = Mock(
            SwitchboardTicket, autospec=True
        )
        mock_otrs_client.create_otrs_process_ticket.return_value.id = 123
        mock_otrs_client.create_otrs_process_ticket.return_value.number = "#123"
        MockOTRSClient.return_value = mock_otrs_client

        ticket = SwitchboardTicket(service_data, customer_data)
        ticket.create()

        mock_otrs_client.create_otrs_process_ticket.assert_called_once()
        self.assertEqual(ticket.id, 123)
        self.assertEqual(ticket.number, "#123")
