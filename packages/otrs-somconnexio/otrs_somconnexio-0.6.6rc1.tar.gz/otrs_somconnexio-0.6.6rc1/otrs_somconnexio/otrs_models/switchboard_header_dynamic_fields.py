# coding: utf-8
from pyotrs.lib import DynamicField


class SwitchboardHeaderDynamicFields:
    def __init__(self, service_data, customer_data, otrs_process_id, otrs_activity_id):
        self.service_data = service_data
        self.customer_data = customer_data
        self.otrs_process_id = otrs_process_id
        self.otrs_activity_id = otrs_activity_id

    def all(self):
        dynamic_fields = [
            self._process_id(),
            self._activity_id(),
            self._is_header(),
            self._first_name(),
            self._name(),
            self._vat_number(),
            self._lang(),
            self._phone(),
            self._mail(),
            self._service_technology(),
            self._sales_team(),
            self._order_id(),
            self._notes(),
        ]

        return [field for field in dynamic_fields if field.value]

    def _process_id(self):
        return DynamicField(
            name="ProcessManagementProcessID", value=self.otrs_process_id
        )

    def _activity_id(self):
        return DynamicField(
            name="ProcessManagementActivityID", value=self.otrs_activity_id
        )

    def _is_header(self):
        return DynamicField(name="CVHeader", value="1")

    def _first_name(self):
        return DynamicField("nomSoci", self.customer_data.first_name)

    def _name(self):
        return DynamicField("cognom1", self.customer_data.name)

    def _vat_number(self):
        return DynamicField(name="NIFNIESoci", value=self.customer_data.vat_number)

    def _lang(self):
        return DynamicField(name="idioma", value=self.customer_data.language)

    def _phone(self):
        return DynamicField(
            name="telefonContacte", value=self.service_data.contact_phone
        )

    def _mail(self):
        return DynamicField(name="correuElectronic", value=self.service_data.email)

    def _service_technology(self):
        return DynamicField(name="TecDelServei", value=self.service_data.technology)

    def _sales_team(self):
        sales_team_dct = {"Residential": "residencial", "Business": "empreses"}
        return DynamicField(
            name="equipVendes",
            value=sales_team_dct.get(self.service_data.sales_team, ""),
        )

    def _order_id(self):
        return DynamicField(name="IDpeticio", value=self.service_data.order_id)

    def _notes(self):
        return DynamicField(
            name="consideracionsActivacio3", value=self.service_data.notes
        )
