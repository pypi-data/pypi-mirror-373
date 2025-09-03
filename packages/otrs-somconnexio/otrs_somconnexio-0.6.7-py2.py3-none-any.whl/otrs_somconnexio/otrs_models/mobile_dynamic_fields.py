from pyotrs.lib import DynamicField

from otrs_somconnexio.otrs_models.provision_dynamic_fields import ProvisionDynamicFields


class MobileDynamicFields(ProvisionDynamicFields):
    def _build_specific_dynamic_fields(self):
        return [
            self._order_id(),
            self._line(),
            self._icc_sc(),
            self._icc_donor(),
            self._service_type(),
            self._previous_provider(),
            self._previous_owner_vat(),
            self._street(),
            self._zip(),
            self._city(),
            self._subdivision(),
            self._sim_received(),
            self._sim_delivery_tracking_code(),
            self._send_sim_type(),
            self._activation_notes(),
            self._delivery_street(),
            self._delivery_zip_code(),
            self._delivery_city(),
            self._delivery_state(),
            self._fiber_linked(),
            self._shared_bond_id(),
            self._confirm_doc(),
        ]

    def _order_id(self):
        return DynamicField("IDpeticio", self.service_data.order_id)

    def _line(self):
        return DynamicField("liniaMobil", self.service_data.phone_number)

    def _icc_sc(self):
        return DynamicField("ICCSC", self.service_data.sc_icc)

    def _icc_donor(self):
        return DynamicField("ICCdonant", self.service_data.icc)

    def _service_type(self):
        if self.service_data.type == "portability":
            return DynamicField("tipusServeiMobil", "portabilitat")
        else:
            return DynamicField("tipusServeiMobil", "altaNova")

    def _previous_provider(self):
        return DynamicField(
            name="operadorDonantMobil", value=self.service_data.previous_provider
        )

    def _previous_owner_vat(self):
        return DynamicField(
            name="dniTitularAnterior", value=self.service_data.previous_owner_vat
        )

    def _activation_notes(self):
        return DynamicField(
            name="consideracionsActivacio", value=self.service_data.activation_notes
        )

    def _sim_received(self):
        sim_recieved = "1" if self.service_data.has_sim else "0"
        return DynamicField("SIMrebuda", sim_recieved)

    def _send_sim_type(self):
        CH_SC_OSO_SIM = "None" if self.service_data.has_sim else "CH_SC_OSO_SIM"
        return DynamicField("tipusEnviamentSIM", CH_SC_OSO_SIM)

    def _sim_delivery_tracking_code(self):
        return DynamicField(
            "CorreusTrackingCode", self.service_data.sim_delivery_tracking_code
        )

    def _street(self):
        return DynamicField("nomVia", self.customer_data.street)

    def _city(self):
        return DynamicField("localitat", self.customer_data.city)

    def _zip(self):
        return DynamicField("codiPostal", self.customer_data.zip)

    def _subdivision(self):
        return DynamicField("provinciaMobil", self.customer_data.subdivision)

    def _delivery_street(self):
        return DynamicField("direccioEnviament", self.service_data.delivery_street)

    def _delivery_city(self):
        return DynamicField("poblacioEnviament", self.service_data.delivery_city)

    def _delivery_zip_code(self):
        return DynamicField("CPenviament", self.service_data.delivery_zip_code)

    def _delivery_state(self):
        return DynamicField("provinciaEnviament", self.service_data.delivery_state)

    def _product(self):
        return DynamicField(name="productMobil", value=self.service_data.product)

    def _fiber_linked(self):
        return DynamicField(
            name="OdooContractRefRelacionat", value=self.service_data.fiber_linked
        )

    def _shared_bond_id(self):
        return DynamicField(
            name="IDAbonamentCompartit", value=self.service_data.shared_bond_id
        )

    def _confirm_doc(self):
        return DynamicField(name="confirmDoc", value="no")
