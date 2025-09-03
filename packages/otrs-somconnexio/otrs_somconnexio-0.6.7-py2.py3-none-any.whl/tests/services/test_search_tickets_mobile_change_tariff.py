import unittest
from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffSharedBondTicketConfiguration,
    ChangeTariffTicketConfiguration,
)

from otrs_somconnexio.services.search_tickets_mobile_change_tariff import (
    SearchMobileChangeTariff,
)
from mock import Mock, patch

customer_code = "123"
df_dct = {
    "liniaMobil": [
        "665195090",
        "726326798",
    ]
}


class SearchTicketsMobileChangeTariffTestCase(unittest.TestCase):
    @patch(
        "otrs_somconnexio.services.search_tickets_mobile_change_tariff.SearchTicketsService",
        return_value=Mock(
            spec=[
                "search",
            ]
        ),
    )
    def test_default_search(self, MockSearchService):
        expected_tickets = [Mock()]
        MockSearchService.return_value.search.return_value = expected_tickets
        result = SearchMobileChangeTariff(customer_code).search(df_dct)
        MockSearchService.assert_called_once_with(
            [
                ChangeTariffTicketConfiguration,
                ChangeTariffSharedBondTicketConfiguration,
            ]
        )
        MockSearchService.return_value.search.assert_called_once_with(
            customer_code,
            [
                ChangeTariffTicketConfiguration.state,
            ],
            df_dct,
        )
        assert result == expected_tickets

    @patch(
        "otrs_somconnexio.services.search_tickets_mobile_change_tariff.SearchTicketsService",
        return_value=Mock(
            spec=[
                "search",
            ]
        ),
    )
    def test_extra_states_search(self, MockSearchService):
        MockSearchService.return_value.search.return_value = [Mock()]
        SearchMobileChangeTariff(customer_code).search(df_dct, ["extra_state"])
        MockSearchService.return_value.search.assert_called_once_with(
            customer_code,
            [
                "extra_state",
                ChangeTariffTicketConfiguration.state,
            ],
            df_dct,
        )

    def test_constructor_configuration(self):
        customer_code = "123"
        instance = SearchMobileChangeTariff(customer_code)
        self.assertEqual(
            instance.search_types[0],
            ChangeTariffTicketConfiguration,
        )
        self.assertEqual(
            instance.search_types[1],
            ChangeTariffSharedBondTicketConfiguration,
        )
        assert instance.search_states[0] == ChangeTariffTicketConfiguration.state
        assert (
            instance.search_states[1] == ChangeTariffSharedBondTicketConfiguration.state
        )
        assert instance.customer_code == customer_code
