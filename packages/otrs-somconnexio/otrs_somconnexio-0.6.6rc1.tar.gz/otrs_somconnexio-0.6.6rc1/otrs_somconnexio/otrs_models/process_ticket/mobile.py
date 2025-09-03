from datetime import datetime

from otrs_somconnexio.otrs_models.process_ticket.process_ticket import ProcessTicket
from otrs_somconnexio.services.mapping_mobile_minutes import ServiceMappingMobileMinutes


class MobileProcessTicket(ProcessTicket):
    @property
    def msisdn(self):
        """Return the assigned number."""
        return self.response.dynamic_field_get("liniaMobil").value

    @property
    def service_type(self):
        """Return the mobile service type."""
        return self.response.dynamic_field_get("tipusServeiMobil").value

    @property
    def data(self):
        return self.response.dynamic_field_get("dadesMobil").value

    @property
    def minutes(self):
        return ServiceMappingMobileMinutes.minutes(
            self.response.dynamic_field_get("minutsMobil").value
        )

    @property
    def icc(self):
        return self.response.dynamic_field_get("ICCSC").value

    @property
    def donor_icc(self):
        return self.response.dynamic_field_get("ICCdonant").value

    @property
    def previous_owner_name(self):
        return self.response.dynamic_field_get("titular").value

    @property
    def previous_owner_surname(self):
        return self.response.dynamic_field_get("cognom1Titular").value

    @property
    def previous_owner_docid(self):
        return self.response.dynamic_field_get("dniTitularAnterior").value

    @property
    def previous_provider(self):
        return self.response.dynamic_field_get("operadorDonantMobil").value

    @property
    def iban(self):
        return self.response.dynamic_field_get("IBAN").value

    @property
    def product_code(self):
        return self.response.dynamic_field_get("productMobil").value

    @property
    def delivery_street(self):
        return self.response.dynamic_field_get("direccioEnviament").value

    @property
    def delivery_city(self):
        return self.response.dynamic_field_get("poblacioEnviament").value

    @property
    def delivery_zip_code(self):
        return self.response.dynamic_field_get("CPenviament").value

    @property
    def delivery_state(self):
        return self.response.dynamic_field_get("provinciaEnviament").value

    @property
    def international_minutes(self):
        return self.response.dynamic_field_get("abonamentInternacional").value

    @property
    def fiber_contract_code(self):
        return self.response.dynamic_field_get("OdooContractRefRelacionat").value

    @property
    def shared_bond_id(self):
        return self.response.dynamic_field_get("IDAbonamentCompartit").value

    @property
    def activation_date(self):
        """Convert the string in a datetime object to be returned"""
        date = self.response.dynamic_field_get("dataActivacioLiniaMobil").value
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    @property
    def mobile_service_type(self):
        return self.response.dynamic_field_get("tipusServeiMobil").value

    @property
    def confirmed_documentation(self):
        return self.response.dynamic_field_get("confirmDoc").value

    def confirmed(self):
        return self.state == "closed successful"

    def cancelled(self):
        return self.state == "closed unsuccessful"

    def paused_without_coverage(self):
        return False
