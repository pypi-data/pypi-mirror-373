# coding: utf-8
import unittest

from pyotrs import Ticket

from otrs_somconnexio.otrs_models.service import Service

from tests.data.otrs_raw_responses import OTRSTicketGetResponse


class ServiceTestCase(unittest.TestCase):
    def test_mobile_coverage(self):
        """
        All the mobile services have coverage.
        """
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "Mobil"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertTrue(service.has_coverage())

    def test_adsl_without_check_coverage(self):
        """
        If the agents haven't checked the coverage yet, the coberturaADSL field is still empty
        """
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "ADSL"},
            {"Name": "coberturaADSL", "Value": None},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertTrue(service.has_coverage())

    def test_adsl_without_coverage(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "ADSL"},
            {"Name": "coberturaADSL", "Value": "NoServei"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertFalse(service.has_coverage())

    def test_adsl100_without_coverage(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "ADSL+100min"},
            {"Name": "coberturaADSL", "Value": "NoServei"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertFalse(service.has_coverage())

    def test_adsl1000_without_coverage(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "ADSL+1000min"},
            {"Name": "coberturaADSL", "Value": "NoServei"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertFalse(service.has_coverage())

    def test_adsl_has_coverage(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "ADSL"},
            {"Name": "coberturaADSL", "Value": "24M"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertTrue(service.has_coverage())

    def test_adsl100_has_coverage(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "ADSL+100min"},
            {"Name": "coberturaADSL", "Value": "24M"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertTrue(service.has_coverage())

    def test_adsl1000_has_coverage(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "ADSL+1000min"},
            {"Name": "coberturaADSL", "Value": "24M"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertTrue(service.has_coverage())

    def test_fibre_without_check_coverage(self):
        """
        If the agents haven't checked the coverage yet, the coberturaFibraMM and coberturaFibraVdf fields are empty.
        """
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "Fibra"},
            {"Name": "coberturaFibraMM", "Value": None},
            {"Name": "coberturaFibraVdf", "Value": None},
            {"Name": "coberturaFibraOrange", "Value": None},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertTrue(service.has_coverage())

    def test_fibre_without_coverage(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "Fibra"},
            {"Name": "coberturaFibraMM", "Value": "NoFibra"},
            {"Name": "coberturaFibraVdf", "Value": "NoFibraVdf"},
            {"Name": "coberturaFibraOrange", "Value": "NoFibra"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertFalse(service.has_coverage())

    def test_fibre_without_coverage_fibra_indirecta(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "Fibra"},
            {"Name": "coberturaFibraMM", "Value": "fibraIndirecta"},
            {"Name": "coberturaFibraVdf", "Value": "NoFibraVdf"},
            {"Name": "coberturaFibraOrange", "Value": "NoFibra"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertFalse(service.has_coverage())

    def test_fibre_has_coverage_MM(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "Fibra"},
            {"Name": "coberturaFibraMM", "Value": "Coaxial"},
            {"Name": "coberturaFibraVdf", "Value": "NoFibraVdf"},
            {"Name": "coberturaFibraOrange", "Value": "NoFibra"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertTrue(service.has_coverage())

    def test_fibre_has_coverage_Orange(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "Fibra"},
            {"Name": "coberturaFibraMM", "Value": "NoFibra"},
            {"Name": "coberturaFibraVdf", "Value": "NoFibraVdf"},
            {"Name": "coberturaFibraOrange", "Value": "FibraFTTH"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertTrue(service.has_coverage())

    def test_fibre_has_coverage_Vdf(self):
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "Fibra"},
            {"Name": "coberturaFibraMM", "Value": "NoFibra"},
            {"Name": "coberturaFibraVdf", "Value": "CoaxialVdf"},
            {"Name": "coberturaFibraOrange", "Value": "NoFibra"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertTrue(service.has_coverage())

    def test_mixed_technology_mobile(self):
        """
        Check technology from a mixted technology mobile ticket.
        """
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "Mixta"},
            {"Name": "tipusServeiMobil", "Value": "Portabilitat"},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertEqual(service._technology, "Mobil")
        self.assertTrue(service.is_mobile())

    def test_mixed_technology_fiber(self):
        """
        Check technology from a mixted technology fiber ticket.
        """
        OTRSTicketGetResponse["DynamicField"] = [
            {"Name": "TecDelServei", "Value": "Mixta"},
            {"Name": "tipusServeiMobil", "Value": ""},
        ]

        service = Service(Ticket(OTRSTicketGetResponse))

        self.assertEqual(service._technology, "Fibra")
        self.assertFalse(service.is_mobile())
