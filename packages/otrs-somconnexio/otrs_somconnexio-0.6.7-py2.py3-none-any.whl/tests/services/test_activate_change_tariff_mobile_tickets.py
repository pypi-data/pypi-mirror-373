import unittest

from mock import Mock, patch
from otrs_somconnexio.services.activate_change_tarriff_mobile_tickets import (
    ActivateChangeTariffMobileTickets,
)


class ActivateChangeTariffMobileTicketsTestCase(unittest.TestCase):
    @patch(
        "otrs_somconnexio.services.base_get_ticket_by_number.OTRSClient",
        return_value=Mock(
            spec=[
                "update_ticket",
                "get_ticket_by_number",
            ]
        ),
    )
    @patch(
        "otrs_somconnexio.services.activate_change_tarriff_mobile_tickets.DynamicField"
    )
    def test_run(self, MockDF, MockOTRSClient):
        ticket_number = "123"
        expected_df = object()
        MockDF.return_value = expected_df
        MockOTRSClient.return_value.get_ticket_by_number.return_value = Mock(
            spec=["tid"]
        )
        MockOTRSClient.return_value.get_ticket_by_number.return_value.tid = 321

        ActivateChangeTariffMobileTickets(ticket_number).run()

        MockOTRSClient.return_value.get_ticket_by_number.assert_called_once_with(
            ticket_number,
            dynamic_fields=True,
        )
        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            MockOTRSClient.return_value.get_ticket_by_number.return_value.tid,
            article=None,
            dynamic_fields=[expected_df],
        )
        MockDF.assert_called_once_with(
            name="enviatMMOV",
            value=1,
        )
