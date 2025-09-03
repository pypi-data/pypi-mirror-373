from otrs_somconnexio.otrs_models.ticket_types.base_customer_ticket import BaseCustomerTicket


class BaseChangeTariffTicketBA(BaseCustomerTicket):

    def _get_specfic_dynamic_fields(self):
        raise NotImplementedError(
            "Tickets to change tariff BA must implement _get_specfic_dynamic_fields"
        )

    def _get_dynamic_fields(self):
        result = {
            **{
                "refOdooContract": self.fields["ref_contract"],
                "telefonFixVell": self.fields["landline_number"],
                "direccioServei": self.fields["service_address"],
                "poblacioServei": self.fields["service_city"],
                "CPservei": self.fields["service_zip"],
                "provinciaServei": self.fields["service_state"],
            },
            **self._get_specfic_dynamic_fields(),
        }
        return result
