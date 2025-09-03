from otrs_somconnexio.otrs_models.ticket_types.base_change_tariff_ba_ticket import (
    BaseChangeTariffTicketBA,
)


class ChangeTariffTicketADSL(BaseChangeTariffTicketBA):
    def _get_specfic_dynamic_fields(self):
        complete_last_name = "%s %s" % (
            self.fields["sur_name"],
            self.fields["last_name"],
        )
        return {
            "serveiPrevi": "ADSL",
            "productBA": self._get_productBA(),
            "nomSoci": self.fields["name"],
            "titular": self.fields["name"],
            "cognom1": complete_last_name,
            "cognom1Titular": complete_last_name,
            "nomCognomSociAntic": self.fields["complete_name"],
            "NIFNIESoci": self.fields["vat_number"],
            "NIFNIEtitular": self.fields["vat_number"],
            "IBAN": self.fields["iban"],
            "telefonFixAntic": self.fields["landline_number"],
            "IDContracte": "-",
            "correuElectronic": self.fields["customer_email"],
            "direccioServeiAntic": "%s - %s %s %s"
            % (
                self.fields["service_address"],
                self.fields["service_zip"],
                self.fields["service_city"],
                self.fields["service_state"],
            ),
            "codiProvinciaServei": self.fields["service_state_code"],
            "telefonContacte": self.fields["customer_phone"],
            "canviUbicacioMateixTitular": "yes",
            "TecDelServei": "ADSL",
        }

    def _get_productBA(self):
        raise NotImplementedError(
            "Tickets to change tariff BA ADSL must implement _get_productBA"
        )
