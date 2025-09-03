# coding: utf-8
import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.mobile_ticket import MobilePausedTicket
from otrs_somconnexio.otrs_models.configurations.provision.mobile_ticket import (
    MobileTicketPausedConfiguration,
)


class MobileTicketPausedTestCase(unittest.TestCase):
    @patch("otrs_somconnexio.otrs_models.provision_ticket.Ticket")
    def test_build_mobile_paused_ticket(self, MockTicket):
        mobile_data = Mock(spec=["order_id", "technology"])
        mobile_data.order_id = 123

        customer_data = Mock(spec=["id"])

        expected_ticket_arguments = {
            "Title": "Ticket#{} - Només mòbil".format(mobile_data.order_id),
            "Type": MobileTicketPausedConfiguration.type,
            "QueueID": MobileTicketPausedConfiguration.queue_id,
            "State": MobileTicketPausedConfiguration.state,
            "SLA": "No pendent resposta",
            "Service": "Mòbil",
            "Priority": MobileTicketPausedConfiguration.priority,
            "CustomerUser": customer_data.id,
            "CustomerID": customer_data.id,
        }

        MobilePausedTicket(mobile_data, customer_data)._build_ticket()

        MockTicket.assert_called_with(expected_ticket_arguments)
