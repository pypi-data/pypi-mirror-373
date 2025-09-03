from otrs_somconnexio.otrs_models.configurations.querys.we_call_you import (
    WeCallYouCATConfiguration,
    WeCallYouCompanyCATConfiguration,
    WeCallYouCompanyESConfiguration,
    WeCallYouESConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.base_customer_ticket import (
    BaseCustomerTicket,
)


class WeCallYouTicket(BaseCustomerTicket):
    def __init__(self, username, customer_code, fields_dict, *args):
        super(WeCallYouTicket, self).__init__(
            username, customer_code, fields_dict, *args
        )
        self.configuration = self._get_congifuration(
            fields_dict["language"], fields_dict["is_company"]
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
            "personaContacte": self.fields["name"],
            "horariTrucada": self.fields["schedule"],
            "telefonContacte": self.fields.get("phone", "").replace(" ", ""),
            "motiuTrucada": self.fields["reason"],
            "referral": self.fields.get("referral"),
            "rgpd": "1",
            "nouEmail": self.fields.get("email"),
            "midaEmpresa": self.fields.get("company_size"),
        }

    def _get_congifuration(self, lang, is_company):
        if lang == "ca_ES":
            if is_company:
                return WeCallYouCompanyCATConfiguration
            return WeCallYouCATConfiguration
        else:
            if is_company:
                return WeCallYouCompanyESConfiguration
            return WeCallYouESConfiguration
