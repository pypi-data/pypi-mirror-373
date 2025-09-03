import unittest

from mock import ANY, Mock, call, patch

from otrs_somconnexio.services.unblock_mobile_pack_ticket import UnblockMobilePackTicket


class UnblockMobilePackTicketTestCase(unittest.TestCase):
    @patch(
        "otrs_somconnexio.services.base_get_ticket_by_number.OTRSClient",
        return_value=Mock(
            spec=[
                "update_ticket",
                "get_ticket_by_number",
            ]
        ),
    )
    @patch("otrs_somconnexio.services.unblock_mobile_pack_ticket.DynamicField")
    def test_run(self, MockDF, MockOTRSClient):
        ticket_number = "123"
        MockOTRSClient.return_value.get_ticket_by_number.return_value = Mock(
            spec=["tid", "dynamic_field_get"]
        )
        MockOTRSClient.return_value.get_ticket_by_number.return_value.tid = 321
        MockOTRSClient.return_value.get_ticket_by_number.return_value.dynamic_field_get.return_value = Mock(
            spec="value"
        )
        MockOTRSClient.return_value.get_ticket_by_number.return_value.dynamic_field_get.return_value.value = (
            0
        )

        UnblockMobilePackTicket(
            ticket_number, activation_date="2022-11-11", introduced_date="2022-11-09"
        ).run()

        MockOTRSClient.return_value.get_ticket_by_number.assert_called_once_with(
            ticket_number,
            dynamic_fields=True,
        )
        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            MockOTRSClient.return_value.get_ticket_by_number.return_value.tid,
            article=None,
            dynamic_fields=[ANY, ANY],
        )
        MockDF.assert_has_calls(
            [
                call(
                    name="recuperarProvisio",
                    value=1,
                ),
                call(
                    name="enviarNotificacio",
                    value=0,
                ),
            ],
            any_order=True,
        )

    @patch(
        "otrs_somconnexio.services.base_get_ticket_by_number.OTRSClient",
        return_value=Mock(
            spec=[
                "update_ticket",
                "get_ticket_by_number",
            ]
        ),
    )
    @patch("otrs_somconnexio.services.unblock_mobile_pack_ticket.DynamicField")
    def test_SIMrebuda(self, MockDF, MockOTRSClient):
        ticket_number = "123"
        expected_df = object()
        MockDF.return_value = expected_df
        MockOTRSClient.return_value.get_ticket_by_number.return_value = Mock(
            spec=["tid", "dynamic_field_get"]
        )
        MockOTRSClient.return_value.get_ticket_by_number.return_value.tid = 321

        def dynamic_field_get_side_effect(key):
            return_value = Mock(spec="value")
            return_value.value = 0
            if key == "SIMrebuda":
                return_value.value = 1
            return return_value

        MockOTRSClient.return_value.get_ticket_by_number.return_value.dynamic_field_get.side_effect = (
            dynamic_field_get_side_effect
        )

        UnblockMobilePackTicket(
            ticket_number, activation_date="2022-11-11", introduced_date="2022-11-09"
        ).run()

        MockOTRSClient.return_value.get_ticket_by_number.assert_called_once_with(
            ticket_number,
            dynamic_fields=True,
        )

        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            MockOTRSClient.return_value.get_ticket_by_number.return_value.tid,
            article=None,
            dynamic_fields=[ANY, ANY, ANY, ANY],
        )
        MockDF.assert_has_calls(
            [
                call(
                    name="recuperarProvisio",
                    value=1,
                ),
                call(
                    name="dataActivacioLiniaMobil",
                    value="2022-11-11",
                ),
                call(
                    name="dataIntroPlataforma",
                    value="2022-11-09",
                ),
                ANY,
            ],
            any_order=True,
        )

    @patch(
        "otrs_somconnexio.services.base_get_ticket_by_number.OTRSClient",
        return_value=Mock(
            spec=[
                "update_ticket",
                "get_ticket_by_number",
            ]
        ),
    )
    @patch("otrs_somconnexio.services.unblock_mobile_pack_ticket.DynamicField")
    def test_dates_already_set_not_overwrite(self, MockDF, MockOTRSClient):
        ticket_number = "123"
        expected_df = object()
        MockDF.return_value = expected_df
        MockOTRSClient.return_value.get_ticket_by_number.return_value = Mock(
            spec=["tid", "dynamic_field_get"]
        )
        MockOTRSClient.return_value.get_ticket_by_number.return_value.tid = 321

        def dynamic_field_get_side_effect(key):
            return_value = Mock(spec="value")
            return_value.value = 0
            if key == "dataIntroPlataforma" or key == "dataActivacioLiniaMobil":
                return_value.value = 1
            return return_value

        MockOTRSClient.return_value.get_ticket_by_number.return_value.dynamic_field_get.side_effect = (
            dynamic_field_get_side_effect
        )

        UnblockMobilePackTicket(
            ticket_number, activation_date="2022-11-11", introduced_date="2022-11-09"
        ).run()

        MockOTRSClient.return_value.get_ticket_by_number.assert_called_once_with(
            ticket_number,
            dynamic_fields=True,
        )

        MockOTRSClient.return_value.update_ticket.assert_not_called()

    @patch(
        "otrs_somconnexio.services.base_get_ticket_by_number.OTRSClient",
        return_value=Mock(
            spec=[
                "update_ticket",
                "get_ticket_by_number",
            ]
        ),
    )
    @patch("otrs_somconnexio.services.unblock_mobile_pack_ticket.DynamicField")
    def test_only_one_date_already_set_overwrite(self, MockDF, MockOTRSClient):
        ticket_number = "123"
        expected_df = object()
        MockDF.return_value = expected_df
        MockOTRSClient.return_value.get_ticket_by_number.return_value = Mock(
            spec=["tid", "dynamic_field_get"]
        )
        MockOTRSClient.return_value.get_ticket_by_number.return_value.tid = 321

        def dynamic_field_get_side_effect(key):
            return_value = Mock(spec="value")
            return_value.value = 0
            if key == "dataIntroPlataforma" or key == "SIMrebuda":
                return_value.value = 1
            return return_value

        MockOTRSClient.return_value.get_ticket_by_number.return_value.dynamic_field_get.side_effect = (
            dynamic_field_get_side_effect
        )

        UnblockMobilePackTicket(
            ticket_number, activation_date="2022-11-11", introduced_date="2022-11-09"
        ).run()

        MockOTRSClient.return_value.get_ticket_by_number.assert_called_once_with(
            ticket_number,
            dynamic_fields=True,
        )

        MockOTRSClient.return_value.update_ticket.assert_called_once_with(
            MockOTRSClient.return_value.get_ticket_by_number.return_value.tid,
            article=None,
            dynamic_fields=[ANY, ANY, ANY, ANY],
        )
        MockDF.assert_has_calls(
            [
                call(
                    name="recuperarProvisio",
                    value=1,
                ),
                call(
                    name="dataActivacioLiniaMobil",
                    value="2022-11-11",
                ),
                call(
                    name="dataIntroPlataforma",
                    value="2022-11-09",
                ),
                ANY,
            ],
            any_order=True,
        )
