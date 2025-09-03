import unittest
from mock import Mock
from faker import Faker

from otrs_somconnexio.otrs_models.switchboard_header_dynamic_fields import (
    SwitchboardHeaderDynamicFields,
)
from .common_helper import dynamic_fields_to_dct


class SwitchboardHeaderDynamicFieldsTestCase(unittest.TestCase):
    def setUp(self):
        faker = Faker("es_CA")

        customer_data = Mock(
            first_name=faker.first_name(),
            name=faker.last_name(),
            vat_number=faker.ssn(),
            has_active_contracts=faker.boolean(),
            language=faker.language_code(),
        )

        self.service_data = Mock(
            notes=faker.text(),
            contact_phone=faker.phone_number(),
            email=faker.email(),
            technology=faker.word(),
            sales_team="Business",
            order_id=faker.uuid4(),
        )

        self.switchboard_otrs_process_id = faker.uuid4()
        self.switchboard_otrs_activity_id = faker.uuid4()

        self.customer_data = customer_data  # Guardem per als tests

        self.dynamic_fields = SwitchboardHeaderDynamicFields(
            self.service_data,
            customer_data,
            self.switchboard_otrs_process_id,
            self.switchboard_otrs_activity_id,
        ).all()

        self.dynamic_fields_dct = dynamic_fields_to_dct(self.dynamic_fields)

    def test_customer_first_name_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["nomSoci"],
            self.customer_data.first_name,
        )

    def test_CV_header_field(self):
        self.assertEqual(self.dynamic_fields_dct["CVHeader"], "1")

    def test_customer_last_name_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["cognom1"],
            self.customer_data.name,
        )

    def test_customer_vat_number_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["NIFNIESoci"],
            self.customer_data.vat_number,
        )

    def test_customer_language_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["idioma"],
            self.customer_data.language,
        )

    def test_customer_phone_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["telefonContacte"],
            self.service_data.contact_phone,
        )

    def test_mail_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["correuElectronic"],
            self.service_data.email,
        )

    def test_service_technology_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["TecDelServei"],
            self.service_data.technology,
        )

    def test_sales_team_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["equipVendes"],
            "empreses",
        )

    def test_order_id_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["IDpeticio"],
            self.service_data.order_id,
        )

    def test_switchboard_otrs_process_id_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["ProcessManagementProcessID"],
            self.switchboard_otrs_process_id,
        )

    def test_switchboard_otrs_activity_id_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["ProcessManagementActivityID"],
            self.switchboard_otrs_activity_id,
        )

    def test_notes_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["consideracionsActivacio3"],
            self.service_data.notes,
        )
