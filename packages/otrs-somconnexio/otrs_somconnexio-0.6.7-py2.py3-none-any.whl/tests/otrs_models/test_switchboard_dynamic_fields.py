import unittest
from mock import Mock
from faker import Faker

from otrs_somconnexio.otrs_models.switchboard_dynamic_fields import (
    SwitchboardDynamicFields,
)
from .common_helper import dynamic_fields_to_dct


class SwitchboardDynamicFieldsTestCase(unittest.TestCase):
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
            order_id=faker.uuid4(),
            iban=faker.iban(),
            email=faker.email(),
            contact_phone=faker.phone_number(),
            product=faker.word(),
            technology=faker.word(),
            sales_team=faker.word(),
            type=faker.word(),
            landline=faker.phone_number(),
            landline_2=faker.phone_number(),
            icc=faker.bban(),
            has_sim=faker.boolean(),
            extension=faker.phone_number(),
            agent_name=faker.name(),
            agent_email=faker.email(),
            previous_owner_vat=faker.ssn(),
            previous_owner_name=faker.first_name(),
            previous_owner_surname=faker.last_name(),
            shipment_address=faker.street_address(),
            shipment_city=faker.city(),
            shipment_zip=faker.zipcode(),
            shipment_subdivision=faker.state(),
        )

        self.switchboard_otrs_process_id = faker.uuid4()
        self.switchboard_otrs_activity_id = faker.uuid4()

        self.dynamic_fields = SwitchboardDynamicFields(
            self.service_data,
            customer_data,
            self.switchboard_otrs_process_id,
            self.switchboard_otrs_activity_id,
        ).all()

        self.dynamic_fields_dct = dynamic_fields_to_dct(self.dynamic_fields)

    def test_process_id_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["ProcessManagementProcessID"],
            self.switchboard_otrs_process_id,
        )

    def test_activity_id_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["ProcessManagementActivityID"],
            self.switchboard_otrs_activity_id,
        )

    def test_product_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["productCV"],
            self.service_data.product,
        )

    def test_extension_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["extensio"],
            self.service_data.extension,
        )

    def test_landline_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["portaFixCV1"],
            self.service_data.landline,
        )

    def test_landline_2_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["portaFixCV2"],
            self.service_data.landline_2,
        )

    def test_ICC_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["ICCSC"],
            self.service_data.icc,
        )

    def test_has_sim_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["SIMrebuda"],
            "1" if self.service_data.has_sim else "0",
        )

    def test_agent_name_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["nomAgentCV"],
            self.service_data.agent_name,
        )

    def test_agent_email_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["correuAgentCV"],
            self.service_data.agent_email,
        )

    def test_shipment_address_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["direccioEnviament"],
            self.service_data.shipment_address,
        )

    def test_shipment_city_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["poblacioEnviament"],
            self.service_data.shipment_city,
        )

    def test_shipment_zip_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["CPenviament"],
            self.service_data.shipment_zip,
        )

    def test_shipment_subdivision_field(self):
        self.assertEqual(
            self.dynamic_fields_dct["provinciaEnviament"],
            self.service_data.shipment_subdivision,
        )

    def test_documentation(self):
        self.assertEqual(
            self.dynamic_fields_dct["flagDocumentacio"],
            "0",
        )
