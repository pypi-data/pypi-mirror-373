# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.switchboard_header_ticket import (
    SwitchboardHeaderTicket,
)
from otrs_somconnexio.otrs_models.configurations.provision.switchboard_ticket import (
    SwitchboardTicketConfiguration,
)


class SwitchboardHeaderTicketTestCase(unittest.TestCase):
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

        SwitchboardHeaderTicket(service_data, customer_data)._build_ticket()
        MockTicket.assert_called_with(expected_ticket_arguments)

    @patch("otrs_somconnexio.otrs_models.provision_ticket.ProvisionArticle")
    def test_build_article(self, MockProvisionArticle):
        service_data = Mock(spec=["order_id", "notes", "technology"])
        service_data.order_id = 123
        service_data.notes = "Notes test"
        customer_data = Mock(spec=["order_id"])

        mock_article = MockProvisionArticle.return_value

        SwitchboardHeaderTicket(service_data, customer_data)._build_article()

        MockProvisionArticle.assert_called_with(
            service_data.technology,
            service_data.order_id,
            "switchboard",
            service_data.notes,
        )
        mock_article.call.assert_called_once()

    @patch(
        "otrs_somconnexio.otrs_models.switchboard_header_ticket.SwitchboardHeaderDynamicFields"
    )
    def test_build_dynamic_fields(self, MockSwitchboardHeaderDynamicFields):
        service_data = Mock()
        customer_data = Mock()
        mock_dyn_fields = MockSwitchboardHeaderDynamicFields.return_value

        SwitchboardHeaderTicket(service_data, customer_data)._build_dynamic_fields()
        MockSwitchboardHeaderDynamicFields.assert_called_with(
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
                "previous_owner_vat",
                "previous_owner_name",
                "previous_owner_surname",
                "sales_team",
                "type",
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
            SwitchboardHeaderTicket, autospec=True
        )
        mock_otrs_client.create_otrs_process_ticket.return_value.id = 123
        mock_otrs_client.create_otrs_process_ticket.return_value.number = "#123"
        MockOTRSClient.return_value = mock_otrs_client

        ticket = SwitchboardHeaderTicket(service_data, customer_data)
        ticket.create()

        mock_otrs_client.create_otrs_process_ticket.assert_called_once()
        self.assertEqual(ticket.id, 123)
        self.assertEqual(ticket.number, "#123")
