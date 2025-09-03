


from otrs_somconnexio.otrs_models.configurations.changes.change_email import ChangeEmailContractsConfiguration
from otrs_somconnexio.otrs_models.ticket_types.change_email_ticket import ChangeEmailTicket

username = "7456787G"
customer_code = "1234"

class TestCaseChangeEmailTicket:
    def test_create(self, mocker):
        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.OTRSClient",
            return_value=mocker.Mock(),
        )
        TicketMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Ticket",
            return_value=mocker.Mock(),
        )  # noqa
        ArticleMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Article",
            return_value=mocker.Mock(),
        )  # noqa
        DynamicFieldMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.DynamicField",
            return_value=mocker.Mock(),
        )  # noqa
        UUIDMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_change_ticket.uuid", spec=["uuid4"]
        )  # noqa
        UUIDMock.uuid4.return_value = "UUID-token"

        expected_ticket_data = {
            "Title": ChangeEmailContractsConfiguration.subject,
            "QueueID": ChangeEmailContractsConfiguration.queue_id,
            "State": ChangeEmailTicket._get_state(self),
            "Type": ChangeEmailTicket._get_type(self),
            "Priority": ChangeEmailTicket._get_priority(self),
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_message = "-"
        expected_article_data = {
            "Subject": ChangeEmailContractsConfiguration.subject,
            "Body": expected_message,
        }

        fields_dict = {
            "new_value": "newemail@email.coop",
            "scope": "some",
            "selected_subscriptions": ["1254"],
            "language": "ca_ES",
        }

        ChangeEmailTicket(
            username,
            customer_code,
            fields_dict,
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        expected_df_calls = [
            mocker.call(
                "ProcessManagementProcessID", ChangeEmailContractsConfiguration.process_id
            ),  # noqa
            mocker.call(
                "ProcessManagementActivityID",
                ChangeEmailContractsConfiguration.activity_id,
            ),  # noqa
            mocker.call("IDOV", UUIDMock.uuid4.return_value),
            mocker.call("refOdooContract", "1254"),
            mocker.call("nouEmail", "newemail@email.coop"),
            mocker.call("flagContracts", True),
            mocker.call("idioma", "ca_ES"),
        ]
        for call in DynamicFieldMock.mock_calls:
            assert call in expected_df_calls

        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for c in expected_df_calls],
            attachments=None,
        )

    def test_create_scope_all(self, mocker):
        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.OTRSClient",
            return_value=mocker.Mock(),
        )
        TicketMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Ticket",
            return_value=mocker.Mock(),
        )  # noqa
        ArticleMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Article",
            return_value=mocker.Mock(),
        )  # noqa
        DynamicFieldMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.DynamicField",
            return_value=mocker.Mock(),
        )  # noqa
        UUIDMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_change_ticket.uuid", spec=["uuid4"]
        )  # noqa
        UUIDMock.uuid4.return_value = "UUID-token"

        expected_ticket_data = {
            "Title": ChangeEmailContractsConfiguration.subject,
            "QueueID": ChangeEmailContractsConfiguration.queue_id,
            "State": ChangeEmailTicket._get_state(self),
            "Type": ChangeEmailTicket._get_type(self),
            "Priority": ChangeEmailTicket._get_priority(self),
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_message = "-"
        expected_article_data = {
            "Subject": ChangeEmailContractsConfiguration.subject,
            "Body": expected_message,
        }

        fields_dict = {
            "new_value": "newemail@email.coop",
            "scope": "all",
            "selected_subscriptions": ["111", "222"],
            "language": "ca_ES",
        }

        ChangeEmailTicket(
            username,
            customer_code,
            fields_dict,
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        expected_df_calls = [
            mocker.call(
                "ProcessManagementProcessID", ChangeEmailContractsConfiguration.process_id
            ),  # noqa
            mocker.call(
                "ProcessManagementActivityID",
                ChangeEmailContractsConfiguration.activity_id,
            ),  # noqa
            mocker.call("IDOV", UUIDMock.uuid4.return_value),
            mocker.call("refOdooContract", "111;222"),
            mocker.call("nouEmail", fields_dict["new_value"]),
            mocker.call("flagContracts", True),
            mocker.call("idioma", "ca_ES"),
        ]
        for call in DynamicFieldMock.mock_calls:
            assert call in expected_df_calls

        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for c in expected_df_calls],
            attachments=None,
        )
