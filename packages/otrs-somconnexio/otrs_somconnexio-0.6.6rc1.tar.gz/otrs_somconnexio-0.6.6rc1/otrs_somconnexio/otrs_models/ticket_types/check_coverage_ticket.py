from otrs_somconnexio.otrs_models.configurations.querys.check_coverage import (
    CheckCoverageCATConfiguration,
    CheckCoverageESConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.base_customer_ticket import (
    BaseCustomerTicket,
)


class CheckCoverageTicket(BaseCustomerTicket):
    def __init__(self, username, customer_code, fields_dict, *args):
        super(CheckCoverageTicket, self).__init__(
            username, customer_code, fields_dict, *args
        )
        self.configuration = (
            CheckCoverageCATConfiguration
            if fields_dict["language"] == "ca_ES"
            else CheckCoverageESConfiguration
        )

    def _get_activity_id(self):
        return self.configuration.activity_id

    def _get_process_id(self):
        return self.configuration.process_id

    def _get_queue_id(self):
        return self.configuration.queue_id

    def _get_subject(self):
        return self.configuration.subject

    def _get_dynamic_fields(self):
        return {
            "nomSoci": self.fields["name"],
            "cognom1": self.fields["surnames"],
            "correuElectronic": self.fields["email"],
            "telefonContacte": self.fields["phone"],
            "idioma": self.fields["contact_lang"],
            "tipusVia": self.fields["road_type"],
            "nomVia": self.fields["road_name"],
            "numero": self.fields["road_number"],
            "bloc": self.fields["block"],
            "portal": self.fields["doorway"],
            "pis": self.fields["floor"],
            "escala": self.fields["scale"],
            "porta": self.fields["door"],
            "altresCobertura": self.fields["other_information"],
            "poblacioServei": self.fields["locality"],
            "provinciaServei": self.fields["state"],
            "CPservei": self.fields["zip_code"],
        }
