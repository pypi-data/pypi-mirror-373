from datetime import datetime
from otrs_somconnexio.services.mapping_services import ServiceMappingServices


class ProcessTicket:
    def __init__(self, otrs_response, service=None):
        self.response = otrs_response
        self.service = service

    @property
    def id(self):
        return self.response.field_get("TicketID")

    @property
    def number(self):
        return self.response.field_get("TicketNumber")

    @property
    def queue(self):
        return self.response.field_get("Queue")

    @property
    def queue_id(self):
        return self.response.field_get("QueueID")

    @property
    def state(self):
        return self.response.field_get("State")

    @property
    def contract_id(self):
        return self.response.dynamic_field_get("IDContracte").value

    # Partner
    @property
    def partner_name(self):
        return self.response.dynamic_field_get("nomSoci").value

    @property
    def partner_surname(self):
        return self.response.dynamic_field_get("cognom1").value

    @property
    def partner_vat_number(self):
        return self.response.dynamic_field_get("NIFNIESoci").value

    # Service
    @property
    def owner_vat_number(self):
        return self.response.dynamic_field_get("NIFNIEtitular").value

    @property
    def iban(self):
        return self.response.dynamic_field_get("IBAN").value

    @property
    def invoices_start_date(self):
        """Convert the string in a datetime object to be returned"""
        invoices_start_date = self.response.dynamic_field_get(
            "dataIniciFacturacio"
        ).value
        return datetime.strptime(invoices_start_date, "%Y-%m-%d %H:%M:%S")

    @property
    def service_technology(self):
        """Return is the service is fiber or adsl"""
        service_tech = self.response.dynamic_field_get("TecDelServei").value
        return ServiceMappingServices.service(service_tech)

    def confirmed(self):
        return self.state == "closed successful"

    def cancelled(self):
        return self.state == "closed unsuccessful"
