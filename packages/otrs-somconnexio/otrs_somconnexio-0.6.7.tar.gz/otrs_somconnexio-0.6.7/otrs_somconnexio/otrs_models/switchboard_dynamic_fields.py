# coding: utf-8
from pyotrs.lib import DynamicField
from otrs_somconnexio.otrs_models.provision_dynamic_fields import ProvisionDynamicFields


class SwitchboardDynamicFields(ProvisionDynamicFields):
    def _build_specific_dynamic_fields(self):
        dynamic_fields = [
            self._type(),
            self._landline(),
            self._landline_2(),
            self._icc(),
            self._sim_received(),
            self._extension(),
            self._agent_name(),
            self._agent_email(),
            self._shipment_address(),
            self._shipment_city(),
            self._shipment_zip(),
            self._shipment_subdivision(),
        ]
        return dynamic_fields

    def _type(self):
        return DynamicField(name="tipusServeiCV", value=self.service_data.type)

    def _product(self):
        return DynamicField(name="productCV", value=self.service_data.product)

    def _landline(self):
        return DynamicField(name="portaFixCV1", value=self.service_data.landline)

    def _landline_2(self):
        return DynamicField(name="portaFixCV2", value=self.service_data.landline_2)

    def _icc(self):
        return DynamicField(name="ICCSC", value=self.service_data.icc)

    def _sim_received(self):
        sim_recieved = "1" if self.service_data.has_sim else "0"
        return DynamicField("SIMrebuda", sim_recieved)

    def _extension(self):
        return DynamicField(name="extensio", value=self.service_data.extension)

    def _agent_name(self):
        return DynamicField(name="nomAgentCV", value=self.service_data.agent_name)

    def _agent_email(self):
        return DynamicField(name="correuAgentCV", value=self.service_data.agent_email)

    def _shipment_address(self):
        return DynamicField(
            name="direccioEnviament", value=self.service_data.shipment_address
        )

    def _shipment_city(self):
        return DynamicField(
            name="poblacioEnviament", value=self.service_data.shipment_city
        )

    def _shipment_zip(self):
        return DynamicField(name="CPenviament", value=self.service_data.shipment_zip)

    def _shipment_subdivision(self):
        return DynamicField(
            name="provinciaEnviament", value=self.service_data.shipment_subdivision
        )
