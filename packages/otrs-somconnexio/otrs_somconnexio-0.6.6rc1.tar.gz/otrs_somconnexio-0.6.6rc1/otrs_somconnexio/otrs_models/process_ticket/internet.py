from otrs_somconnexio.otrs_models.process_ticket.mobile import MobileProcessTicket
from otrs_somconnexio.otrs_models.process_ticket.process_ticket import ProcessTicket


class InternetProcessTicket(ProcessTicket):
    @property
    def previous_provider(self):
        return self.response.dynamic_field_get("proveidorPrevi").value

    @property
    def service_address(self):
        return self.response.dynamic_field_get("direccioServei").value

    @property
    def service_city(self):
        return self.response.dynamic_field_get("poblacioServei").value

    @property
    def service_subdivision(self):
        return self.response.dynamic_field_get("provinciaServei").value

    @property
    def service_subdivision_code(self):
        return self.response.dynamic_field_get("codiProvinciaServei").value

    @property
    def service_zip(self):
        return self.response.dynamic_field_get("CPservei").value

    @property
    def extid(self):
        """
        ADSL: IDcomanda ?
        Fiber: IDhogar ?
        """
        if (
            self.response.dynamic_field_get("IDcomanda").value
            and self.response.dynamic_field_get("IDhogar").value
        ):
            # TODO: Log possible error?
            pass
        if self.response.dynamic_field_get("IDcomanda").value:
            return self.response.dynamic_field_get("IDcomanda").value
        elif self.response.dynamic_field_get("IDhogar").value:
            return self.response.dynamic_field_get("IDhogar").value

    @property
    def mac_address(self):
        return self.response.dynamic_field_get("MACaddress").value

    @property
    def reference(self):
        """
        ADSL: numAdministratiuJazztel
        Fiber: pon
        """
        if (
            self.response.dynamic_field_get("pon").value
            and self.response.dynamic_field_get("numAdministratiuJazztel").value
        ):
            # TODO: Log possible error?
            pass
        if self.response.dynamic_field_get("pon").value:
            return self.response.dynamic_field_get("pon").value
        elif self.response.dynamic_field_get("numAdministratiuJazztel").value:
            return self.response.dynamic_field_get("numAdministratiuJazztel").value

    @property
    def endpoint_user(self):
        return self.response.dynamic_field_get("usuariEndpoint").value

    @property
    def endpoint_password(self):
        return self.response.dynamic_field_get("contrasenyaEndpoint").value

    @property
    def ppp_user(self):
        return self.response.dynamic_field_get("usuariPPP").value

    @property
    def ppp_password(self):
        return self.response.dynamic_field_get("serialNumber").value

    @property
    def msisdn(self):
        """Return the assigned number."""
        return self.response.dynamic_field_get("telefonFixAssignat").value

    # ADSL
    @property
    def landline(self):
        return self.response.dynamic_field_get("serveiFix").value

    @property
    def landline_minutes(self):
        return self.response.dynamic_field_get("minutsInclosos").value

    @property
    def keep_landline_number(self):
        return self.response.dynamic_field_get("mantenirFix").value

    # Fiber
    @property
    def speed(self):
        return self.response.dynamic_field_get("velocitatSollicitada").value

    @property
    def icc(self):
        return MobileProcessTicket(self.response).icc

    @property
    def product_code(self):
        return self.response.dynamic_field_get("productBA").value

    def paused_without_coverage(self):
        return not self.service.has_coverage()
