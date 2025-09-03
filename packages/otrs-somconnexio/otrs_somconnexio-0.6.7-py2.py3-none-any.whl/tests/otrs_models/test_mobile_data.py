# coding: utf-8
import unittest

from otrs_somconnexio.otrs_models.mobile_data import MobileData


class MobileDataTestCase(unittest.TestCase):
    def test_init(self):
        mobile_data = MobileData(
            order_id=123,
            contact_phone="666666661",
            phone_number="666666666",
            iban="ES6621000418401234567891",
            email="test@test.com",
            previous_provider="SC",
            previous_owner_vat="740227654G",
            previous_owner_name="name",
            previous_owner_surname="surname",
            type="new",
            sc_icc="123456789",
            icc=None,
            product="product",
            notes="Mobile crm lead line",
            activation_notes="More notes",
            has_sim=True,
            delivery_street="Les Moreres",
            delivery_city="Alacant",
            delivery_zip_code="03140",
            delivery_state="ES-A",
            technology="Mòbil",
            sales_team="residential",
            sim_delivery_tracking_code="325",
        )

        self.assertIsInstance(mobile_data, MobileData)
