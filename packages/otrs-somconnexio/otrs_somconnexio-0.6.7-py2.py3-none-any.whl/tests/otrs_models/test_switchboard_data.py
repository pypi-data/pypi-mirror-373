# coding: utf-8
import unittest

from otrs_somconnexio.otrs_models.switchboard_data import SwitchboardData


class SwitchboardDataTestCase(unittest.TestCase):
    def test_init(self):
        switchboard_data = SwitchboardData(
            order_id="1234567890",
            iban="ES6621000418401234567891",
            email="test@test.com",
            contact_phone="666666661",
            product="product",
            technology="switchboard",
            sales_team="Business",
            type="new",
            landline="999888777",
            landline_2="999888778",
            extension="123",
            agent_name="agent1",
            agent_email="agent1@company.org",
            icc="123456789",
            has_sim=True,
            previous_owner_vat="ES12345678A",
            previous_owner_name="name",
            previous_owner_surname="surname",
            shipment_address="address",
            shipment_city="city",
            shipment_zip="08001",
            shipment_subdivision="ES-B",
            notes="Notes",
            activation_notes="More notes",
        )

        self.assertIsInstance(switchboard_data, SwitchboardData)
