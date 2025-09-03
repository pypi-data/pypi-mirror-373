# coding: utf-8
import os
import unittest
from mock import Mock, patch

from pyotrs.lib import DynamicField
from pyotrs.lib import APIError
from otrs_somconnexio.client import OTRSClient
from otrs_somconnexio.otrs_models.process_ticket.internet import InternetProcessTicket
from otrs_somconnexio.otrs_models.process_ticket.mobile import MobileProcessTicket
from otrs_somconnexio.exceptions import (
    ErrorCreatingSession,
    TicketNotCreated,
    TicketNotFoundError,
)

USER = "user"
PASSW = "passw"
URL = "https://otrs-url.coop/"


@patch.dict(os.environ, {"OTRS_USER": USER, "OTRS_PASSW": PASSW, "OTRS_URL": URL})
class ClientTestCase(unittest.TestCase):
    @patch("otrs_somconnexio.client.Client")
    def test_error_creating_session(self, MockClient):
        def mock_client_constructor(
            baseurl, username, password, webservice_config_ticket
        ):
            raise APIError("Example error")

        MockClient.side_effect = mock_client_constructor

        self.assertRaisesRegex(
            ErrorCreatingSession,
            "Error creating the session with the next error message: Example error",
            OTRSClient,
        )

    @patch("otrs_somconnexio.client.OTRSCreationTicketResponse")
    @patch("otrs_somconnexio.client.Client")
    def test_create_otrs_process_ticket(
        self, MockClient, MockOTRSCreationTicketResponse
    ):
        expected_ticket = Mock(spec=[])
        expected_article = Mock(spec=[])
        expected_dynamic_fields = Mock(spec=[])

        expected_client_response = Mock(spec=[])

        def mock_ticket_create(ticket, article, dynamic_fields, attachments):
            if (
                ticket == expected_ticket
                and article == expected_article
                and dynamic_fields == expected_dynamic_fields
                and attachments == None
            ):
                return expected_client_response

        mock_client = Mock(spec=["session_create", "ticket_create"])
        mock_client.ticket_create = mock_ticket_create

        def mock_client_constructor(
            baseurl, username, password, webservice_config_ticket
        ):
            if (
                username == USER
                and baseurl == URL
                and password == PASSW
            ):
                return mock_client

        MockClient.side_effect = mock_client_constructor

        OTRSClient().create_otrs_process_ticket(
            expected_ticket, expected_article, expected_dynamic_fields
        )

        MockOTRSCreationTicketResponse.assert_called_once_with(expected_client_response)

    @patch("otrs_somconnexio.client.Client")
    def test_create_otrs_process_ticket_error_ticket_not_created(self, MockClient):
        ticket = Mock(spec=[])
        article = Mock(spec=[])
        dynamic_fields = [(DynamicField(name="sample-df", value="value-df"))]
        attachments = None
        error_msg = "Example error"

        def mock_ticket_create(ticket, article, dynamic_fields, attachments):
            raise APIError(error_msg)

        mock_client = Mock(spec=["session_create", "ticket_create"])
        mock_client.ticket_create = mock_ticket_create
        MockClient.return_value = mock_client
        shown_msg = "{}\n\t{}\n{}".format(
            "Error creating the ticket with the next error message:",
            error_msg,
            "sample-df: value-df",
        )

        self.assertRaisesRegex(
            TicketNotCreated,
            shown_msg,
            OTRSClient().create_otrs_process_ticket,
            ticket,
            article,
            dynamic_fields,
        )

    @patch("otrs_somconnexio.client.Service")
    @patch("otrs_somconnexio.client.InternetProcessTicket")
    @patch("otrs_somconnexio.client.Client")
    def test_get_otrs_process_ticket(
        self, MockClient, MockInternetProcessTicket, MockService
    ):
        expected_ticket_id = 123

        mock_ticket = Mock(spec=[])

        service = Mock(spec=["is_mobile"])
        service.is_mobile.return_value = False
        MockService.return_value = service

        def mock_ticket_get_by_id(ticket_id, dynamic_fields):
            if ticket_id == expected_ticket_id and dynamic_fields is True:
                return mock_ticket

        mock_client = Mock(spec=["session_create", "ticket_get_by_id"])
        mock_client.ticket_get_by_id = mock_ticket_get_by_id

        def mock_client_constructor(
            baseurl, username, password, webservice_config_ticket
        ):
            if (
                username == USER
                and baseurl == URL
                and password == PASSW
            ):
                return mock_client

        MockClient.side_effect = mock_client_constructor

        OTRSClient().get_otrs_process_ticket(expected_ticket_id)

        MockInternetProcessTicket.assert_called_once_with(mock_ticket, service)

    @patch("otrs_somconnexio.client.Client")
    def test_get_otrs_process_ticket_ticket_not_found(self, MockClient):
        def mock_ticket_get_by_id(ticket_id, dynamic_fields):
            return False

        mock_client = Mock(spec=["session_create", "ticket_get_by_id"])
        mock_client.ticket_get_by_id = mock_ticket_get_by_id
        MockClient.return_value = mock_client

        self.assertRaisesRegex(
            TicketNotFoundError,
            "Error searching the ticket with ID 1234 with the next error message: ",
            OTRSClient().get_otrs_process_ticket,
            1234,
        )

    @patch("otrs_somconnexio.client.Service")
    @patch("otrs_somconnexio.client.Client")
    def test_search_tickets(self, MockClient, MockService):
        params = {"hola": 123}
        ticket_one = Mock(spec=[])
        ticket_two = Mock(spec=[])
        service = Mock(spec=["is_mobile"])
        service.is_mobile.return_value = False
        MockService.return_value = service
        expected_tickets = [
            InternetProcessTicket(ticket_one, service),
            InternetProcessTicket(ticket_two, service),
        ]

        def mock_ticket_get_by_id(ticket_id, dynamic_fields):
            if ticket_id == 1 and dynamic_fields is True:
                return ticket_one
            elif ticket_id == 2 and dynamic_fields is True:
                return ticket_two

        mock_client = Mock(spec=["session_create", "ticket_search", "ticket_get_by_id"])
        mock_client.ticket_get_by_id = mock_ticket_get_by_id
        mock_client.ticket_search.return_value = [1, 2]

        def mock_client_constructor(
            baseurl, username, password, webservice_config_ticket
        ):
            if (
                username == USER
                and baseurl == URL
                and password == PASSW
            ):
                return mock_client

        MockClient.side_effect = mock_client_constructor

        tickets = OTRSClient().search_tickets(**params)

        mock_client.ticket_search.assert_called_once_with(**params)
        self.assertEqual(len(expected_tickets), len(tickets))
        self.assertEqual(expected_tickets[0].__dict__, tickets[0].__dict__)
        self.assertEqual(expected_tickets[1].__dict__, tickets[1].__dict__)

    @patch("otrs_somconnexio.client.DynamicField")
    @patch("otrs_somconnexio.client.Client")
    def test_search_coverage_tickets_by_email(self, MockClient, MockDynamicField):
        email = "email@test.org"
        process_df = MockDynamicField()
        email_df = MockDynamicField()
        expected_dynamic_fields = [process_df, email_df]

        def dynamic_field_side_effect(name, search_patterns):
            if name == "ProcessManagementProcessID" and search_patterns == [
                "Process-be8cf222949132c9fae1bb74615a5ae4"
            ]:
                return process_df
            if name == "correuElectronic" and search_patterns == [email]:
                return email_df

        MockDynamicField.side_effect = dynamic_field_side_effect

        otrs_client = OTRSClient()
        otrs_client.search_tickets = Mock(spec=[], return_value=[])

        otrs_client.search_coverage_tickets_by_email(email)

        otrs_client.search_tickets.assert_called_once_with(
            dynamic_fields=expected_dynamic_fields
        )

    @patch("otrs_somconnexio.client.Client")
    def test_update_ticket(self, MockClient):
        ticket_id = 123
        article = Mock(spec=[])
        sample_df = [DynamicField(name="sample-df", value="value-df")]

        mock_client = Mock(spec=["session_create", "ticket_update"])

        def mock_client_constructor(
            baseurl, username, password, webservice_config_ticket
        ):
            if (
                username == USER
                and baseurl == URL
                and password == PASSW
            ):
                return mock_client

        MockClient.side_effect = mock_client_constructor

        OTRSClient().update_ticket(ticket_id, article, sample_df)

        mock_client.ticket_update.assert_called_once_with(
            ticket_id, article, dynamic_fields=sample_df
        )

    @patch("otrs_somconnexio.client.Service")
    @patch("otrs_somconnexio.client.Client")
    def test_get_ticket_by_number(self, MockClient, MockService):
        ticket_number = "A0123"
        ticket = Mock(spec=[])
        service = Mock(spec=["is_mobile"])
        service.is_mobile.return_value = True
        MockService.return_value = service
        expected_ticket = MobileProcessTicket(ticket, service)

        def mock_ticket_get_by_number(ticket_number, dynamic_fields):
            if ticket_number == ticket_number and dynamic_fields is False:
                return expected_ticket

        mock_client = Mock(spec=["session_create", "ticket_get_by_number"])
        mock_client.ticket_get_by_number.side_effect = mock_ticket_get_by_number

        def mock_client_constructor(
            baseurl, username, password, webservice_config_ticket
        ):
            if (
                username == USER
                and baseurl == URL
                and password == PASSW
            ):
                return mock_client

        MockClient.side_effect = mock_client_constructor

        obtained_ticket = OTRSClient().get_ticket_by_number(ticket_number)

        mock_client.ticket_get_by_number.assert_called_once_with(
            ticket_number, dynamic_fields=False
        )
        self.assertEqual(obtained_ticket, expected_ticket)
        self.assertIsInstance(obtained_ticket, MobileProcessTicket)

    @patch("otrs_somconnexio.client.Client")
    def test_link_tickets(self, MockClient):
        ticket_src_id = 123
        ticket_dst_id = 456
        link_type = "ParentChild"

        mock_client = Mock(spec=["session_create", "link_add"])

        def mock_client_constructor(
            baseurl, username, password, webservice_config_ticket
        ):
            if (
                username == USER
                and baseurl == URL
                and password == PASSW
            ):
                return mock_client

        MockClient.side_effect = mock_client_constructor

        OTRSClient().link_tickets(ticket_src_id, ticket_dst_id, link_type=link_type)

        mock_client.link_add.assert_called_once_with(
            ticket_src_id, ticket_dst_id, link_type=link_type
        )

    @patch("otrs_somconnexio.client.Client")
    @patch("otrs_somconnexio.client.OTRSClient.get_otrs_process_ticket")
    def test_get_link_list_tickets(self, mock_get_otrs_proces_ticket, MockClient):
        ticket_src_id = 123
        link_type = "Normal"
        first_ticket_id = "11822"
        second_ticket_id = "11823"
        expected_response = [
            {
                "Type": "Normal",
                "Key": first_ticket_id,
                "Object": "Ticket",
                "Direction": "Source",
            },
            {
                "Type": "Normal",
                "Key": second_ticket_id,
                "Object": "Ticket",
                "Direction": "Source",
            },
        ]
        mock_client = Mock(spec=["session_create", "link_list"])
        mock_first_ticket = object()
        mock_second_ticket = object()

        def mock_client_constructor(
            baseurl, username, password, webservice_config_ticket
        ):
            if (
                username == USER
                and baseurl == URL
                and password == PASSW
            ):
                return mock_client

        MockClient.side_effect = mock_client_constructor
        mock_client.link_list.return_value = expected_response

        def mock_get_otrs_process_ticket(ticket_id):
            if ticket_id == first_ticket_id:
                return mock_first_ticket
            elif ticket_id == second_ticket_id:
                return mock_second_ticket

        mock_get_otrs_proces_ticket.side_effect = mock_get_otrs_process_ticket

        tickets = OTRSClient().get_linked_tickets(ticket_src_id, link_type=link_type)

        mock_client.link_list.assert_called_once_with(
            src_object_id=ticket_src_id, link_type=link_type
        )
        self.assertEqual(tickets, [mock_first_ticket, mock_second_ticket])

    @patch("otrs_somconnexio.client.Client")
    @patch("otrs_somconnexio.client.OTRSClient.get_otrs_process_ticket")
    def test_get_link_list_one_ticket(self, mock_get_otrs_proces_ticket, MockClient):
        ticket_src_id = 123
        link_type = "Normal"
        expected_ticket_id = "11822"
        expected_response = {
            "Type": "Normal",
            "Key": expected_ticket_id,
            "Object": "Ticket",
            "Direction": "Source",
        }

        mock_client = Mock(spec=["session_create", "link_list"])
        mock_first_ticket = object()

        def mock_client_constructor(
            baseurl, username, password, webservice_config_ticket
        ):
            if (
                username == USER
                and baseurl == URL
                and password == PASSW
            ):
                return mock_client

        MockClient.side_effect = mock_client_constructor
        mock_client.link_list.return_value = expected_response

        def mock_get_otrs_process_ticket(ticket_id):
            if ticket_id == expected_ticket_id:
                return mock_first_ticket

        mock_get_otrs_proces_ticket.side_effect = mock_get_otrs_process_ticket

        tickets = OTRSClient().get_linked_tickets(ticket_src_id, link_type=link_type)

        mock_client.link_list.assert_called_once_with(
            src_object_id=ticket_src_id, link_type=link_type
        )
        self.assertEqual(tickets, [mock_first_ticket])

    @patch("otrs_somconnexio.client.Client")
    def test_get_link_list_no_tickets(self, MockClient):
        ticket_src_id = 123
        link_type = "Normal"
        expected_response = None
        mock_client = Mock(spec=["session_create", "link_list"])

        def mock_client_constructor(
            baseurl, username, password, webservice_config_ticket
        ):
            if (
                username == USER
                and baseurl == URL
                and password == PASSW
            ):
                return mock_client

        MockClient.side_effect = mock_client_constructor
        mock_client.link_list.return_value = expected_response

        tickets = OTRSClient().get_linked_tickets(ticket_src_id, link_type=link_type)

        mock_client.link_list.assert_called_once_with(
            src_object_id=ticket_src_id, link_type=link_type
        )
        self.assertEqual(tickets, [])
