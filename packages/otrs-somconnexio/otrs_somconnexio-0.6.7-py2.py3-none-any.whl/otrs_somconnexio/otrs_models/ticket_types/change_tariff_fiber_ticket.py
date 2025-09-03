from otrs_somconnexio.otrs_models.configurations.changes.change_tariff_fiber import (
    ChangeTariffTicketFiberConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.base_change_tariff_ba_ticket import (
    BaseChangeTariffTicketBA,
)


class ChangeTariffTicketFiber(BaseChangeTariffTicketBA):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(ChangeTariffTicketFiber, self).__init__(
            username, customer_code, fields_dict, override_ticket_ids, fallback_path
        )
        self.configuration = ChangeTariffTicketFiberConfiguration

    def _get_subject(self):
        return self.configuration.subject

    def _get_queue_id(self):
        return self.configuration.queue_id

    def _get_specfic_dynamic_fields(self):
        return {
            "serveiPrevi": "Fibra",
            "productBA": self._get_product_ba(),
            "dataExecucioCanviTarifa": self.fields["effective_date"],
            "TecDelServei": "Fibra",
        }

    def _get_product_ba(self):
        return (
            self.configuration.code_fiber_100
            if self.fields["previous_service"]
            == self.configuration.code_fiber_100_landline
            else self.configuration.code_fiber_300
        )
