from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffExceptionalTicketConfiguration,
    ChangeTariffSharedBondTicketConfiguration,
    ChangeTariffTicketConfiguration,
)

from .base_customer_ticket import BaseCustomerTicket


class ChangeTariffTicket(BaseCustomerTicket):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(ChangeTariffTicket, self).__init__(
            username, customer_code, fields_dict, override_ticket_ids, fallback_path
        )
        self.configuration = ChangeTariffTicketConfiguration()

    def _get_subject(self):
        return "Sol·licitud Canvi de tarifa oficina virtual"

    def _get_queue_id(self):
        return self.configuration.queue_id

    def _get_dynamic_fields(self):
        return {
            "renovaCanviTarifa": self._transform_boolean_df(self.override_ticket_ids),
            "liniaMobil": self.fields["phone_number"],
            "productMobil": self.fields["new_product_code"],
            "tarifaAntiga": self.fields["current_product_code"],
            "dataExecucioCanviTarifa": self.fields["effective_date"],
            "OdooContractRefRelacionat": self.fields["fiber_linked"],
            "correuElectronic": self.fields["subscription_email"],
            "idioma": self.fields["language"],
            "enviarNotificacio": self._transform_boolean_df(
                self.fields.get("send_notification", "1")
            ),
            "TecDelServei": "Mobil",
        }


class ChangeTariffExceptionalTicket(ChangeTariffTicket):
    def __init__(self, service_data, customer_data, otrs_configuration=None):
        super().__init__(service_data, customer_data, otrs_configuration)
        self.configuration = ChangeTariffExceptionalTicketConfiguration()

    def _get_subject(self):
        return "Sol·licitud Canvi de tarifa excepcional"


class ChangeTariffMobilePackTicket(ChangeTariffTicket):
    def _get_subject(self):
        return "Sol·licitud canvi de tarifa pack apinyades"

    def _get_dynamic_fields(self):
        dynamic_fields = super()._get_dynamic_fields()
        dynamic_fields.update(
            {"creadorAbonament": bool(self.fields.get("pack_creator", False))}
        )
        return dynamic_fields


class ChangeTariffSharedBondTicket(ChangeTariffMobilePackTicket):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
    ):
        super().__init__(username, customer_code, fields_dict, override_ticket_ids)
        self.configuration = ChangeTariffSharedBondTicketConfiguration()

    def _get_subject(self):
        return "Sol·licitud canvi de tarifa pack amb dades compartides"

    def _get_dynamic_fields(self):
        dynamic_fields = super()._get_dynamic_fields()
        dynamic_fields.update(
            {"IDAbonamentCompartit": self.fields.get("shared_bond_id", "")}
        )
        return dynamic_fields
