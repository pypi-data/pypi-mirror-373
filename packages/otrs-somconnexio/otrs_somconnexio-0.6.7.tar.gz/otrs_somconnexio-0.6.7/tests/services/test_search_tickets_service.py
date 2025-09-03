import unittest

from mock import Mock, patch, call

from otrs_somconnexio.services.search_tickets_service import SearchTicketsService
from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffTicketConfiguration,
)
from otrs_somconnexio.otrs_models.configurations.provision.fiber_ticket import (
    FiberTicketConfiguration,
)


class SearchTicketsServiceTestCase(unittest.TestCase):
    @patch(
        "otrs_somconnexio.services.search_tickets_service.OTRSClient",
        return_value=Mock(
            spec=[
                "search_tickets",
            ]
        ),
    )
    @patch("otrs_somconnexio.services.search_tickets_service.DynamicField")
    def test_search(self, MockDF, MockOTRSClient):
        customer_code = "123"
        state_list = ["new", "open"]
        df_dct = {
            "productMobil": [
                "SE_SC_REC_MOBILE_PACK_UNL_20480",
                "SE_SC_REC_MOBILE_T_UNL_1024",
            ]
        }
        service = SearchTicketsService(ChangeTariffTicketConfiguration)
        calls = [
            call(
                "ProcessManagementProcessID",
                search_patterns=[ChangeTariffTicketConfiguration.process_id],
            ),
            call(
                "ProcessManagementActivityID",
                search_patterns=[ChangeTariffTicketConfiguration.activity_id],
            ),
            call("productMobil", search_patterns=df_dct["productMobil"]),
        ]
        expected_df = object()
        MockDF.return_value = expected_df
        expected_search_args = {
            "dynamic_fields": [expected_df, expected_df, expected_df],
            "QueueIDs": [ChangeTariffTicketConfiguration.queue_id],
            "CustomerID": customer_code,
            "States": state_list,
        }

        self.assertIn(ChangeTariffTicketConfiguration, service.configurations)
        service.search(
            customer_code=customer_code, state_list=state_list, df_dct=df_dct
        )

        MockDF.assert_has_calls(calls)

        MockOTRSClient.return_value.search_tickets.assert_called_once_with(
            **expected_search_args
        )

    @patch(
        "otrs_somconnexio.services.search_tickets_service.OTRSClient",
        return_value=Mock(
            spec=[
                "search_tickets",
            ]
        ),
    )
    @patch("otrs_somconnexio.services.search_tickets_service.DynamicField")
    def test_search_no_customer_code_no_extra_df(self, MockDF, MockOTRSClient):
        state_list = ["new", "open"]
        service = SearchTicketsService(ChangeTariffTicketConfiguration)
        calls = [
            call(
                "ProcessManagementProcessID",
                search_patterns=[ChangeTariffTicketConfiguration.process_id],
            ),
            call(
                "ProcessManagementActivityID",
                search_patterns=[ChangeTariffTicketConfiguration.activity_id],
            ),
        ]
        expected_df = object()
        MockDF.return_value = expected_df
        expected_search_args = {
            "dynamic_fields": [expected_df, expected_df],
            "QueueIDs": [ChangeTariffTicketConfiguration.queue_id],
            "States": state_list,
        }

        self.assertIn(ChangeTariffTicketConfiguration, service.configurations)
        service.search(state_list=state_list)

        MockDF.assert_has_calls(calls)

        MockOTRSClient.return_value.search_tickets.assert_called_once_with(
            **expected_search_args
        )

    @patch(
        "otrs_somconnexio.services.search_tickets_service.OTRSClient",
        return_value=Mock(
            spec=[
                "search_tickets",
            ]
        ),
    )
    @patch("otrs_somconnexio.services.search_tickets_service.DynamicField")
    def test_search_multiple_configurations(self, MockDF, MockOTRSClient):
        customer_code = "123"
        state_list = ["new", "open"]
        df_dct = {
            "productMobil": [
                "SE_SC_REC_MOBILE_PACK_UNL_20480",
                "SE_SC_REC_MOBILE_T_UNL_1024",
            ]
        }

        service = SearchTicketsService(
            [FiberTicketConfiguration, ChangeTariffTicketConfiguration]
        )

        self.assertIn(FiberTicketConfiguration, service.configurations)
        self.assertIn(ChangeTariffTicketConfiguration, service.configurations)

        calls = [
            call(
                "ProcessManagementProcessID",
                search_patterns=[
                    FiberTicketConfiguration.process_id,
                    ChangeTariffTicketConfiguration.process_id,
                ],
            ),
            call(
                "ProcessManagementActivityID",
                search_patterns=[
                    FiberTicketConfiguration.activity_id,
                    ChangeTariffTicketConfiguration.activity_id,
                ],
            ),
            call("productMobil", search_patterns=df_dct["productMobil"]),
        ]
        expected_df = object()
        MockDF.return_value = expected_df
        expected_search_args = {
            "dynamic_fields": [expected_df, expected_df, expected_df],
            "QueueIDs": [
                FiberTicketConfiguration.queue_id,
                ChangeTariffTicketConfiguration.queue_id,
            ],
            "CustomerID": customer_code,
            "States": state_list,
        }

        self.assertIn(ChangeTariffTicketConfiguration, service.configurations)
        service.search(customer_code, state_list, df_dct)

        MockDF.assert_has_calls(calls)

        MockOTRSClient.return_value.search_tickets.assert_called_once_with(
            **expected_search_args
        )
