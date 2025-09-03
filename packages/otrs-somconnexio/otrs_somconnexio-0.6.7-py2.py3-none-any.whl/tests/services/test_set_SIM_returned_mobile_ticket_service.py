import unittest

from mock import ANY, Mock, call, patch

from otrs_somconnexio.services.set_SIM_returned_mobile_ticket import (
    SetSIMReturnedMobileTicket,
)


@patch("otrs_somconnexio.services.set_SIM_returned_mobile_ticket.DynamicField")
@patch("otrs_somconnexio.services.set_SIM_returned_mobile_ticket.SIMReturnedArticle")
@patch("otrs_somconnexio.services.base_get_ticket_by_number.OTRSClient")
class SetSIMReturnedMobileTicketTestCase(unittest.TestCase):
    def setUp(self):
        self.mock_otrs_client = Mock(
            spec=[
                "update_ticket",
                "get_ticket_by_number",
            ]
        )

    def test_run(self, MockOTRSClient, MockSIMReturnedArticle, MockDF):
        ticket_number = "123"
        MockOTRSClient.return_value = self.mock_otrs_client
        MockOTRSClient.return_value.get_ticket_by_number.return_value = Mock(
            spec=["tid"]
        )

        SetSIMReturnedMobileTicket(ticket_number).run()

        MockOTRSClient.return_value.get_ticket_by_number.assert_called_once_with(
            ticket_number,
            dynamic_fields=True,
        )
        MockDF.assert_has_calls(
            [
                call(
                    name="referenciaCorreus",
                    value="",
                ),
                call(
                    name="SIMrebuda",
                    value=0,
                ),
            ]
        )
        MockOTRSClient.return_value.update_ticket.assert_has_calls(
            [
                call(
                    MockOTRSClient.return_value.get_ticket_by_number.return_value.tid,
                    article=None,
                    dynamic_fields=[ANY, ANY],
                ),
                call(
                    MockOTRSClient.return_value.get_ticket_by_number.return_value.tid,
                    article=MockSIMReturnedArticle.return_value.call.return_value,
                ),
            ]
        )
