# coding: utf-8
from otrs_somconnexio.otrs_models.provision_ticket import ProvisionTicket
from otrs_somconnexio.otrs_models.switchboard_dynamic_fields import (
    SwitchboardDynamicFields,
)
from otrs_somconnexio.otrs_models.configurations.provision.switchboard_ticket import (
    SwitchboardTicketConfiguration,
)


class SwitchboardTicket(ProvisionTicket):
    def __init__(self, service_data, customer_data):
        self.service_data = service_data
        self.customer_data = customer_data
        self.otrs_configuration = SwitchboardTicketConfiguration()

    def service_type(self):
        return "switchboard"

    def _build_dynamic_fields(self):
        return SwitchboardDynamicFields(
            self.service_data,
            self.customer_data,
            self._ticket_process_id(),
            self._ticket_activity_id(),
        ).all()
