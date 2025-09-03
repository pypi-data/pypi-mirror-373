


from otrs_somconnexio.otrs_models.configurations.changes.change_iban import ChangeIbanTicketConfiguration
from otrs_somconnexio.otrs_models.ticket_types.change_iban_ticket import ChangeIbanTicket


class TestCaseChangeIbanTicket:
    def test_create(self, mocker):
        username = "7456787G"
        customer_code = "1234"
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
            "Title": ChangeIbanTicketConfiguration.subject,
            "QueueID": ChangeIbanTicketConfiguration.queue_id,
            "State": ChangeIbanTicket._get_state(self),
            "Type": ChangeIbanTicket._get_type(self),
            "Priority": ChangeIbanTicket._get_priority(self),
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_message = "-"
        expected_article_data = {
            "Subject": ChangeIbanTicketConfiguration.subject,
            "Body": expected_message,
        }

        fields_dict = {
            "new_value": "ES6621000418401234567891",
            "scope": "all",
            "selected_subscriptions": ["1254"],
            "language": "ca_ES"
        }

        ChangeIbanTicket(username, customer_code,
            fields_dict,
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        expected_df_calls = [
            mocker.call("nouIBAN", fields_dict["new_value"]),
            mocker.call(
                "ProcessManagementProcessID", ChangeIbanTicketConfiguration.process_id
            ),  # noqa
            mocker.call(
                "ProcessManagementActivityID",
                ChangeIbanTicketConfiguration.activity_id
            ),  # noqa
            mocker.call("IDOV", UUIDMock.uuid4.return_value),
            mocker.call("refOdooContract", "1254"),
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
