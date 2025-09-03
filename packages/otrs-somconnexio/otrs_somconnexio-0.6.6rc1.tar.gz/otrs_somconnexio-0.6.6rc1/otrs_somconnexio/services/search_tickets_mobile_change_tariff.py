from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffSharedBondTicketConfiguration,
    ChangeTariffTicketConfiguration,
)
from otrs_somconnexio.services.search_tickets_service import SearchTicketsService


class SearchMobileChangeTariff:
    def __init__(self, customer_code):
        self.search_types = [
            ChangeTariffTicketConfiguration,
            ChangeTariffSharedBondTicketConfiguration,
        ]
        self.search_states = [
            ChangeTariffTicketConfiguration.state,
            ChangeTariffSharedBondTicketConfiguration.state,
        ]
        self.customer_code = customer_code

    def search(self, df_dct, extra_states=[]):
        states = sorted(list(set(self.search_states + extra_states)))
        tickets_found = SearchTicketsService(self.search_types).search(
            self.customer_code, states, df_dct
        )
        return tickets_found
