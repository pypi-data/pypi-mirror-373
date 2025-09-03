# coding: utf-8
import unittest
from mock import patch, Mock

from otrs_somconnexio.otrs_models.ticket_factory import TicketFactory
from otrs_somconnexio.exceptions import ServiceTypeNotAllowedError


class TicketFactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.customer_data = Mock(spec=[])
        self.service_data = Mock(spec=["order_id", "type", "is_grouped_with_fiber"])

    @patch("otrs_somconnexio.otrs_models.ticket_factory.MobileTicket")
    def test_build_mobile_ticket(self, MockMobileTicket):
        self.service_data.service_type = "mobile"
        self.service_data.is_grouped_with_fiber = False

        TicketFactory(self.service_data, self.customer_data).build()

        MockMobileTicket.assert_called_once_with(
            service_data=self.service_data, customer_data=self.customer_data
        )

    @patch("otrs_somconnexio.otrs_models.ticket_factory.MobilePausedTicket")
    def test_build_mobile_paused_ticket_portability(self, MockMobilePausedTicket):
        self.service_data.service_type = "mobile"
        self.service_data.type = "portability"
        self.service_data.is_grouped_with_fiber = True

        TicketFactory(self.service_data, self.customer_data).build()

        MockMobilePausedTicket.assert_called_once_with(
            service_data=self.service_data, customer_data=self.customer_data
        )

    @patch("otrs_somconnexio.otrs_models.ticket_factory.MobilePausedTicket")
    def test_build_mobile_paused_ticket_fiber_linked(self, MockMobilePausedTicket):
        self.service_data.service_type = "mobile"
        self.service_data.type = "new"
        self.service_data.is_grouped_with_fiber = True
        self.service_data.is_from_pack = True

        TicketFactory(self.service_data, self.customer_data).build()

        MockMobilePausedTicket.assert_called_once_with(
            service_data=self.service_data, customer_data=self.customer_data
        )

    @patch("otrs_somconnexio.otrs_models.ticket_factory.ADSLTicket")
    def test_build_adsl_ticket(self, MockADSLTicket):
        self.service_data.service_type = "adsl"

        TicketFactory(self.service_data, self.customer_data).build()

        MockADSLTicket.assert_called_once_with(
            service_data=self.service_data, customer_data=self.customer_data
        )

    @patch("otrs_somconnexio.otrs_models.ticket_factory.FiberTicket")
    def test_build_fibre_ticket(self, MockFiberTicket):
        self.service_data.service_type = "fiber"

        TicketFactory(self.service_data, self.customer_data).build()

        MockFiberTicket.assert_called_once_with(
            service_data=self.service_data, customer_data=self.customer_data
        )

    def test_build_service_not_allowed_error(self):
        self.service_data.service_type = ""

        ticket_factory = TicketFactory(self.service_data, self.customer_data)

        self.assertRaises(ServiceTypeNotAllowedError, ticket_factory.build)
