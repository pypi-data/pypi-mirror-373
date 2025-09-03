import unittest
from mock import Mock

from otrs_somconnexio.otrs_models.mobile_dynamic_fields import MobileDynamicFields
from .common_helper import dynamic_fields_to_dct


class MobileDynamicFieldsTestCase(unittest.TestCase):
    def setUp(self):
        self.customer_data = Mock(
            spec=[
                "id",
                "vat_number",
                "name",
                "first_name",
                "street",
                "zip",
                "city",
                "subdivision",
                "has_active_contracts",
                "language",
            ]
        )
        self.mobile_data = Mock(
            spec=[
                "order_id",
                "contact_phone",
                "phone_number",
                "iban",
                "email",
                "sc_icc",
                "icc",
                "service_internet_unlimited",
                "type",
                "previous_owner_vat",
                "previous_owner_name",
                "previous_owner_surname",
                "previous_provider",
                "product",
                "has_sim",
                "sim_delivery_tracking_code",
                "type",
                "delivery_street",
                "delivery_city",
                "delivery_zip_code",
                "delivery_state",
                "activation_notes",
                "technology",
                "sales_team",
                "fiber_linked",
                "shared_bond_id",
            ]
        )
        self.mobile_data.type = "new"
        self.mobile_otrs_process_id = "MobileProcessID"
        self.mobile_otrs_activity_id = "MobileActivityID"

    def test_process_id_field(self):
        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(
            dynamic_fields_dct["ProcessManagementProcessID"], "MobileProcessID"
        )

    def test_activity_id_field(self):
        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(
            dynamic_fields_dct["ProcessManagementActivityID"], "MobileActivityID"
        )

    def test_first_name_field(self):
        self.customer_data.first_name = "First Name"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["nomSoci"], "First Name")

    def test_name_field(self):
        self.customer_data.name = "Name"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["cognom1"], "Name")

    def test_vat_number_field(self):
        self.customer_data.vat_number = "NIFCode"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["NIFNIESoci"], "NIFCode")

    def test_has_active_contracts_field(self):
        self.customer_data.has_active_contracts = True

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["teContractesActius"], "1")

    def test_has_active_contracts_false_field(self):
        self.customer_data.has_active_contracts = False

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["teContractesActius"], "0")

    def test_language_field(self):
        self.customer_data.language = "ca_ES"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["idioma"], "ca_ES")

    def test_order_id_field(self):
        self.mobile_data.order_id = "2222"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["IDpeticio"], "2222")

    def test_line_field(self):
        self.mobile_data.phone_number = "666666666"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["liniaMobil"], "666666666")

    def test_icc_sc_field(self):
        self.mobile_data.sc_icc = "1234"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["ICCSC"], "1234")

    def test_icc_donor_field(self):
        self.mobile_data.icc = "4321"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["ICCdonant"], "4321")

    def test_service_type_field_new(self):
        self.mobile_data.type = "new"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["tipusServeiMobil"], "altaNova")

    def test_service_type_field_portability(self):
        self.mobile_data.type = "portability"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["tipusServeiMobil"], "portabilitat")

    def test_service_has_sim(self):
        self.mobile_data.has_sim = True

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["SIMrebuda"], "1")
        self.assertEqual(dynamic_fields_dct["tipusEnviamentSIM"], "None")

    def test_service_does_not_have_sim(self):
        self.mobile_data.has_sim = False

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["SIMrebuda"], "0")
        self.assertEqual(dynamic_fields_dct["tipusEnviamentSIM"], "CH_SC_OSO_SIM")

    def test_IBAN_field(self):
        self.mobile_data.iban = "ES6621000418401234567891"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["IBAN"], "ES6621000418401234567891")

    def test_contact_email_field(self):
        self.mobile_data.email = "test@email.org"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["correuElectronic"], "test@email.org")

    def test_contact_phone_field(self):
        self.mobile_data.contact_phone = "666666666"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["telefonContacte"], "666666666")

    def test_previous_provider_field(self):
        self.mobile_data.previous_provider = "AireNubip"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["operadorDonantMobil"], "AireNubip")

    # Portability
    def test_previous_owner_vat_portability(self):
        self.mobile_data.previous_owner_vat = "1234G"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["dniTitularAnterior"], "1234G")

    def test_previous_owner_name_portability(self):
        self.mobile_data.previous_owner_name = "Josep"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["titular"], "Josep")

    def test_previous_owner_first_name_portability(self):
        self.mobile_data.previous_owner_surname = "Nadal"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["cognom1Titular"], "Nadal")

    def test_product_field(self):
        self.mobile_data.product = "SE_SC_MOB_100_100"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["productMobil"], "SE_SC_MOB_100_100")

    def test_street_field(self):
        self.customer_data.street = "Les Moreres"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["nomVia"], "Les Moreres")

    def test_city_field(self):
        self.customer_data.city = "Alacant"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["localitat"], "Alacant")

    def test_zip_field(self):
        self.customer_data.zip = "03140"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["codiPostal"], "03140")

    def test_subdivision_field(self):
        self.customer_data.subdivision = "ES-A"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["provinciaMobil"], "ES-A")

    def test_delivery_street_field(self):
        self.mobile_data.delivery_street = "Les Moreres"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["direccioEnviament"], "Les Moreres")

    def test_delivery_city_field(self):
        self.mobile_data.delivery_city = "Alacant"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["poblacioEnviament"], "Alacant")

    def test_delivery_zip_code_field(self):
        self.mobile_data.delivery_zip_code = "03140"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["CPenviament"], "03140")

    def test_delivery_state_field(self):
        self.mobile_data.delivery_state = "ES-A"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["provinciaEnviament"], "ES-A")

    def test_activation_notes_field(self):
        self.mobile_data.activation_notes = "text text text"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(
            dynamic_fields_dct["consideracionsActivacio"], "text text text"
        )

    def test_tecnhology(self):
        self.mobile_data.technology = "Mòbil"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["TecDelServei"], "Mòbil")

    def test_sales_team(self):
        self.mobile_data.sales_team = "Residential"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["equipVendes"], "residencial")

    def test_fiber_linked(self):
        self.mobile_data.fiber_linked = "72"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["OdooContractRefRelacionat"], "72")

    def test_shared_bond_id(self):
        self.mobile_data.shared_bond_id = "A72"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["IDAbonamentCompartit"], "A72")

    def test_sim_delivery_tracking_code(self):
        self.mobile_data.sim_delivery_tracking_code = "72"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["CorreusTrackingCode"], "72")

    def test_documentation(self):
        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["flagDocumentacio"], "0")

    def test_confirm_doc(self):
        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id,
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["confirmDoc"], "no")
