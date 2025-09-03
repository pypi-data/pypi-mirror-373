# coding: utf-8
import unittest

from otrs_somconnexio.otrs_models.switchboard_header_data import SwitchboardHeaderData


class SwitchboardHeaderDataTestCase(unittest.TestCase):
    def test_init(self):
        sb_header_data = SwitchboardHeaderData(
            order_id=123,
            contact_phone="666666661",
            email="test@test.com",
            sales_team="residential",
            technology="switchboard",
            notes="Notes",
        )

        self.assertIsInstance(sb_header_data, SwitchboardHeaderData)
