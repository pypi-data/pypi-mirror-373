from otrs_somconnexio.otrs_models.configurations.changes.change_tariff_adsl import (
    ChangeTariffTicketAdslOutLandlineConfig,
)
from otrs_somconnexio.otrs_models.ticket_types.change_tariff_adsl_ticket import (
    ChangeTariffTicketADSL,
)


class ChangeTariffOutLandLineADSL(ChangeTariffTicketADSL):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(ChangeTariffOutLandLineADSL, self).__init__(
            username, customer_code, fields_dict, override_ticket_ids, fallback_path
        )
        self.configuration = ChangeTariffTicketAdslOutLandlineConfig

    def _get_queue_id(self):
        return self.configuration.queue_id

    def _get_subject(self):
        return self.configuration.subject

    def _get_productBA(self):
        return self.configuration.code_fiber
