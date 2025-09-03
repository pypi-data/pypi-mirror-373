import unittest

from mock import ANY, Mock, patch

from otrs_somconnexio.services.get_mobile_related_tickets import GetMobileRelatedTickets


class GetMobileRelatedTicketsTestCase(unittest.TestCase):
    @patch(
        "otrs_somconnexio.services.base_get_ticket_by_number.OTRSClient",
        return_value=Mock(
            spec=[
                "get_ticket_by_number",
                "get_linked_tickets",
            ]
        ),
    )
    def test_run(self, MockOTRSClient):
        ticket_number = "123"
        MockOTRSClient.return_value.get_ticket_by_number.return_value = Mock(
            spec=["tid"]
        )
        MockOTRSClient.return_value.get_ticket_by_number.return_value.tid = 321
        MockOTRSClient.return_value.get_linked_tickets.return_value = [ANY, ANY]

        related_tickets = GetMobileRelatedTickets(ticket_number).run()

        MockOTRSClient.return_value.get_ticket_by_number.assert_called_once_with(
            ticket_number,
            dynamic_fields=True,
        )
        MockOTRSClient.return_value.get_linked_tickets.assert_called_once_with(
            MockOTRSClient.return_value.get_ticket_by_number.return_value.tid,
            "Normal",
        )
        assert (
            related_tickets
            == MockOTRSClient.return_value.get_linked_tickets.return_value
        )
