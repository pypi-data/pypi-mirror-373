# coding: utf-8
from pyotrs.lib import DynamicField

from otrs_somconnexio.otrs_models.internet_dynamic_fields import InternetDynamicFields


class FiberDynamicFields(InternetDynamicFields):
    def _build_specific_broadband_service_dynamic_fields(self):
        """Return list of OTRS DynamicFields to create a OTRS Process Ticket from service data and customer data.
        Return only the specifics fields of Fiber Ticket."""
        return [
            self._df_previous_contract_pon(),
            self._df_previous_contract_fiber_speed(),
            self._activation_notes(),
            self._df_mobile_pack_contracts(),
            self._df_all_grouped_SIMS_recieved(),
            self._df_has_previous_owner_with_mobile_pack_contracts(),
            self._df_product_ba_mm(),
            self._keep_landline_number(),
        ]

    def _activation_notes(self):
        return DynamicField(
            name="consideracionsActivacio2", value=self.service_data.activation_notes
        )

    def _df_previous_contract_pon(self):
        return DynamicField(
            name="ponAntic", value=self.service_data.previous_contract_pon
        )

    def _df_previous_contract_fiber_speed(self):
        return DynamicField(
            name="velocitatSollicitadaContracteAnteriorCU",
            value=self.service_data.previous_contract_fiber_speed,
        )

    def _df_mobile_pack_contracts(self):
        return DynamicField(
            name="OdooMobileContractRefRelacionats",
            value=self.service_data.mobile_pack_contracts,
        )

    def _df_all_grouped_SIMS_recieved(self):
        are_all_grouped_SIMS_recieved = (
            "1" if self.service_data.all_grouped_SIMS_recieved else "0"
        )
        return DynamicField(
            name="SIMrebuda",
            value=are_all_grouped_SIMS_recieved,
        )

    def _df_has_previous_owner_with_mobile_pack_contracts(self):
        has_grouped_mobile_with_previous_owner = (
            "1" if self.service_data.has_grouped_mobile_with_previous_owner else "0"
        )
        return DynamicField(
            name="flagDNItitularAnteriorMobils",
            value=has_grouped_mobile_with_previous_owner,
        )

    def _df_product_ba_mm(self):
        return DynamicField(name="productBAMM", value=self.service_data.product_ba_mm)

    def _keep_landline_number(self):
        if self.service_data.keep_landline:
            value = "current_number"
        else:
            value = "new_number"
        return DynamicField(name="mantenirFix", value=value)
