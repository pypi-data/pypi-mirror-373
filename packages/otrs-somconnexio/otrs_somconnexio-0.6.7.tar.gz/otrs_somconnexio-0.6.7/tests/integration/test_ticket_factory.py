import unittest
from mock import Mock, patch

from otrs_somconnexio.otrs_models.ticket_factory import TicketFactory
from otrs_somconnexio.otrs_models.adsl_ticket import ADSLTicket
from otrs_somconnexio.otrs_models.fiber_ticket import FiberTicket
from otrs_somconnexio.otrs_models.mobile_ticket import MobileTicket, MobilePausedTicket
from otrs_somconnexio.otrs_models.router_4G_ticket import Router4GTicket
from otrs_somconnexio.otrs_models.switchboard_ticket import SwitchboardTicket


class TicketFactoryIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.customer_data = Mock(
            spec=[
                "id",
                "first_name",
                "name",
                "vat_number",
                "street",
                "city",
                "zip",
                "subdivision",
                "has_active_contracts",
                "language",
            ]
        )

    @patch("otrs_somconnexio.otrs_models.provision_ticket.OTRSClient")
    def test_create_mobile_ticket_factory(self, MockOTRSClient):
        mobile_data = Mock(
            spec=[
                "order_id",
                "type",
                "iban",
                "email",
                "contact_phone",
                "phone_number",
                "sc_icc",
                "icc",
                "type",
                "previous_provider",
                "previous_owner_name",
                "previous_owner_surname",
                "previous_owner_vat",
                "product",
                "notes",
                "has_sim",
                "sim_delivery_tracking_code",
                "is_grouped_with_fiber",
                "delivery_street",
                "delivery_city",
                "delivery_zip_code",
                "delivery_state",
                "activation_notes",
                "technology",
                "sales_team",
                "is_from_pack",
                "fiber_linked",
                "shared_bond_id",
            ]
        )

        mobile_data.service_type = "mobile"

        otrs_process_ticket = Mock(spec=["id"])
        otrs_process_ticket.id = 234

        mock_otrs_client = Mock(spec=["create_otrs_process_ticket"])
        mock_otrs_client.create_otrs_process_ticket.return_value = otrs_process_ticket
        MockOTRSClient.return_value = mock_otrs_client

        ticket = TicketFactory(
            service_data=mobile_data, customer_data=self.customer_data
        ).build()
        ticket.create()

        self.assertEqual(ticket.id, 234)
        self.assertIsInstance(ticket, MobileTicket)

    @patch("otrs_somconnexio.otrs_models.provision_ticket.OTRSClient")
    def test_create_mobile_portability_paused_ticket_factory(self, MockOTRSClient):
        mobile_data = Mock(
            spec=[
                "order_id",
                "iban",
                "email",
                "contact_phone",
                "phone_number",
                "sc_icc",
                "icc",
                "type",
                "previous_provider",
                "previous_owner_name",
                "previous_owner_surname",
                "previous_owner_vat",
                "product",
                "notes",
                "has_sim",
                "sim_delivery_tracking_code",
                "is_grouped_with_fiber",
                "delivery_street",
                "delivery_city",
                "delivery_zip_code",
                "delivery_state",
                "activation_notes",
                "technology",
                "sales_team",
                "is_from_pack",
                "fiber_linked",
                "shared_bond_id",
            ]
        )

        mobile_data.service_type = "mobile"
        mobile_data.type = "portability"
        mobile_data.is_grouped_with_fiber = True

        otrs_process_ticket = Mock(spec=["id"])
        otrs_process_ticket.id = 234

        mock_otrs_client = Mock(spec=["create_otrs_process_ticket"])
        mock_otrs_client.create_otrs_process_ticket.return_value = otrs_process_ticket
        MockOTRSClient.return_value = mock_otrs_client

        ticket = TicketFactory(
            service_data=mobile_data,
            customer_data=self.customer_data,
        ).build()
        ticket.create()

        self.assertEqual(ticket.id, 234)
        self.assertIsInstance(ticket, MobilePausedTicket)

    @patch("otrs_somconnexio.otrs_models.provision_ticket.OTRSClient")
    def test_create_mobile_is_from_pack_paused_ticket_factory(self, MockOTRSClient):
        mobile_data = Mock(
            spec=[
                "order_id",
                "iban",
                "email",
                "contact_phone",
                "phone_number",
                "sc_icc",
                "icc",
                "type",
                "previous_provider",
                "previous_owner_name",
                "previous_owner_surname",
                "previous_owner_vat",
                "product",
                "notes",
                "has_sim",
                "sim_delivery_tracking_code",
                "is_grouped_with_fiber",
                "delivery_street",
                "delivery_city",
                "delivery_zip_code",
                "delivery_state",
                "activation_notes",
                "technology",
                "sales_team",
                "is_from_pack",
                "fiber_linked",
                "shared_bond_id",
            ]
        )

        mobile_data.service_type = "mobile"
        mobile_data.is_grouped_with_fiber = True
        mobile_data.is_from_pack = True

        otrs_process_ticket = Mock(spec=["id"])
        otrs_process_ticket.id = 234

        mock_otrs_client = Mock(spec=["create_otrs_process_ticket"])
        mock_otrs_client.create_otrs_process_ticket.return_value = otrs_process_ticket
        MockOTRSClient.return_value = mock_otrs_client

        ticket = TicketFactory(
            service_data=mobile_data,
            customer_data=self.customer_data,
        ).build()
        ticket.create()

        self.assertEqual(ticket.id, 234)
        self.assertIsInstance(ticket, MobilePausedTicket)

    @patch("otrs_somconnexio.otrs_models.provision_ticket.OTRSClient")
    def test_create_adsl_ticket_factory(self, MockOTRSClient):
        service_data = Mock(
            spec=[
                "order_id",
                "type",
                "iban",
                "email",
                "contact_phone",
                "phone_number",
                "keep_landline",
                "previous_provider",
                "previous_owner_name",
                "previous_owner_surname",
                "previous_owner_vat",
                "previous_service",
                "previous_contract_address",
                "previous_contract_phone",
                "service_address",
                "service_city",
                "service_zip",
                "service_subdivision",
                "service_subdivision_code",
                "shipment_address",
                "shipment_city",
                "shipment_zip",
                "shipment_subdivision",
                "notes",
                "activation_notes",
                "adsl_coverage",
                "mm_fiber_coverage",
                "asociatel_fiber_coverage",
                "orange_fiber_coverage",
                "vdf_fiber_coverage",
                "type",
                "landline_phone_number",
                "product",
                "previous_internal_provider",
                "technology",
                "sales_team",
            ]
        )

        service_data.service_type = "adsl"

        otrs_process_ticket = Mock(spec=["id"])
        otrs_process_ticket.id = 234

        mock_otrs_client = Mock(spec=["create_otrs_process_ticket"])
        mock_otrs_client.create_otrs_process_ticket.return_value = otrs_process_ticket
        MockOTRSClient.return_value = mock_otrs_client

        ticket = TicketFactory(service_data, self.customer_data).build()
        ticket.create()
        ticket.create()

        self.assertIsInstance(ticket, ADSLTicket)
        self.assertEqual(ticket.id, 234)

    @patch("otrs_somconnexio.otrs_models.provision_ticket.OTRSClient")
    def test_create_fiber_ticket_factory(self, MockOTRSClient):
        service_data = Mock(
            spec=[
                "order_id",
                "previous_contract_pon",
                "previous_contract_fiber_speed",
                "previous_contract_address",
                "previous_contract_phone",
                "type",
                "iban",
                "email",
                "contact_phone",
                "phone_number",
                "keep_landline",
                "previous_provider",
                "previous_owner_name",
                "previous_owner_surname",
                "previous_owner_vat",
                "previous_service",
                "service_address",
                "service_city",
                "service_zip",
                "service_subdivision",
                "service_subdivision_code",
                "shipment_address",
                "shipment_city",
                "shipment_zip",
                "shipment_subdivision",
                "notes",
                "activation_notes",
                "adsl_coverage",
                "mm_fiber_coverage",
                "asociatel_fiber_coverage",
                "orange_fiber_coverage",
                "vdf_fiber_coverage",
                "type",
                "product",
                "previous_internal_provider",
                "mobile_pack_contracts",
                "all_grouped_SIMS_recieved",
                "has_grouped_mobile_with_previous_owner",
                "technology",
                "sales_team",
                "product_ba_mm",
            ]
        )

        service_data.service_type = "fiber"

        otrs_process_ticket = Mock(spec=["id"])
        otrs_process_ticket.id = 234

        mock_otrs_client = Mock(spec=["create_otrs_process_ticket"])
        mock_otrs_client.create_otrs_process_ticket.return_value = otrs_process_ticket
        MockOTRSClient.return_value = mock_otrs_client

        ticket = TicketFactory(service_data, self.customer_data).build()
        ticket.create()

        self.assertIsInstance(ticket, FiberTicket)
        self.assertEqual(ticket.id, 234)

    @patch("otrs_somconnexio.otrs_models.provision_ticket.OTRSClient")
    def test_create_router_4G_ticket_factory(self, MockOTRSClient):
        service_data = Mock(
            spec=[
                "order_id",
                "previous_provider",
                "previous_owner_name",
                "previous_owner_surname",
                "previous_owner_vat",
                "previous_service",
                "previous_contract_address",
                "previous_contract_phone",
                "previous_internal_provider",
                "service_address",
                "service_city",
                "service_zip",
                "service_subdivision",
                "service_subdivision_code",
                "shipment_address",
                "shipment_city",
                "shipment_zip",
                "shipment_subdivision",
                "adsl_coverage",
                "mm_fiber_coverage",
                "asociatel_fiber_coverage",
                "orange_fiber_coverage",
                "vdf_fiber_coverage",
                "type",
                "iban",
                "email",
                "contact_phone",
                "phone_number",
                "notes",
                "activation_notes",
                "product",
                "technology",
                "sales_team",
            ]
        )

        service_data.service_type = "4G"

        otrs_process_ticket = Mock(spec=["id"])
        otrs_process_ticket.id = 234

        mock_otrs_client = Mock(spec=["create_otrs_process_ticket"])
        mock_otrs_client.create_otrs_process_ticket.return_value = otrs_process_ticket
        MockOTRSClient.return_value = mock_otrs_client

        ticket = TicketFactory(service_data, self.customer_data).build()
        ticket.create()

        self.assertIsInstance(ticket, Router4GTicket)
        self.assertEqual(ticket.id, 234)

    @patch("otrs_somconnexio.otrs_models.provision_ticket.OTRSClient")
    def test_create_switchboard_ticket_factory(self, MockOTRSClient):
        service_data = Mock(
            spec=[
                "order_id",
                "technology",
                "sales_team",
                "type",
                "iban",
                "email",
                "contact_phone",
                "product",
                "landline",
                "landline_2",
                "agent_name",
                "agent_email",
                "previous_owner_name",
                "previous_owner_surname",
                "extension",
                "icc",
                "has_sim",
                "shipment_address",
                "shipment_city",
                "shipment_zip",
                "shipment_subdivision",
                "notes",
                "activation_notes",
            ]
        )

        service_data.service_type = "switchboard"

        otrs_process_ticket = Mock(spec=["id"])
        otrs_process_ticket.id = 234

        mock_otrs_client = Mock(spec=["create_otrs_process_ticket"])
        mock_otrs_client.create_otrs_process_ticket.return_value = otrs_process_ticket
        MockOTRSClient.return_value = mock_otrs_client

        ticket = TicketFactory(service_data, self.customer_data).build()
        ticket.create()

        self.assertIsInstance(ticket, SwitchboardTicket)
        self.assertEqual(ticket.id, 234)
