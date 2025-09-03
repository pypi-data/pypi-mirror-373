# coding: utf-8

from pyotrs.lib import DynamicField


class ProvisionDynamicFields:
    def __init__(self, service_data, customer_data, otrs_process_id, otrs_activity_id):
        self.service_data = service_data
        self.customer_data = customer_data
        self.otrs_process_id = otrs_process_id
        self.otrs_activity_id = otrs_activity_id

    def all(self):
        dynamic_fields = [
            self._process_id(),
            self._activity_id(),
            self._first_name(),
            self._name(),
            self._vat_number(),
            self._iban(),
            self._phone(),
            self._mail(),
            self._previous_owner_name(),
            self._previous_owner_surname1(),
            self._previous_owner_full_name(),
            self._product(),
            self._service_technology(),
            self._sales_team(),
            self._has_active_contracts(),
            self._has_documentation(),
            self._lang(),
        ]
        dynamic_fields += self._build_specific_dynamic_fields()

        return [field for field in dynamic_fields if field.value]

    def _process_id(self):
        return DynamicField(
            name="ProcessManagementProcessID", value=self.otrs_process_id
        )

    def _activity_id(self):
        return DynamicField(
            name="ProcessManagementActivityID", value=self.otrs_activity_id
        )

    def _first_name(self):
        return DynamicField("nomSoci", self.customer_data.first_name)

    def _name(self):
        return DynamicField("cognom1", self.customer_data.name)

    def _vat_number(self):
        return DynamicField(name="NIFNIESoci", value=self.customer_data.vat_number)

    def _has_active_contracts(self):
        has_active_contacts = "1" if self.customer_data.has_active_contracts else "0"
        return DynamicField(name="teContractesActius", value=has_active_contacts)

    def _lang(self):
        return DynamicField(name="idioma", value=self.customer_data.language)

    def _mail(self):
        return DynamicField(name="correuElectronic", value=self.service_data.email)

    def _phone(self):
        return DynamicField(
            name="telefonContacte", value=self.service_data.contact_phone
        )

    def _iban(self):
        return DynamicField("IBAN", self.service_data.iban)

    def _previous_owner_name(self):
        return DynamicField(name="titular", value=self.service_data.previous_owner_name)

    def _previous_owner_surname1(self):
        return DynamicField(
            name="cognom1Titular", value=self.service_data.previous_owner_surname
        )

    def _previous_owner_full_name(self):
        full_name = ""
        if self.service_data.type == "location_change":
            full_name = "{} {}".format(
                self.service_data.previous_owner_name,
                self.service_data.previous_owner_surname,
            )
        return DynamicField(name="nomCognomSociAntic", value=full_name)

    def _service_technology(self):
        return DynamicField(name="TecDelServei", value=self.service_data.technology)

    def _sales_team(self):
        """odoo crm model team_id field mapping"""
        sales_team_dct = {
            "Residential": "residencial",
            "Business": "empreses",
            "Sales": "vendes",
        }
        return DynamicField(
            name="equipVendes",
            value=sales_team_dct.get(self.service_data.sales_team, ""),
        )

    def _has_documentation(self):
        return DynamicField(name="flagDocumentacio", value="0")
