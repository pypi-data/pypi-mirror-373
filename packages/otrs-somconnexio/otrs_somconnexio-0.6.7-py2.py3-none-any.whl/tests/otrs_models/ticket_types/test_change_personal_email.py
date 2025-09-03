

from otrs_somconnexio.otrs_models.configurations.changes.change_email import ChangeEmailPersonalConfiguration
from otrs_somconnexio.otrs_models.ticket_types.change_personal_email_ticket import ChangePersonalEmailTicket


class TestCaseChangePersonalEmail:
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
            "otrs_somconnexio.otrs_models.ticket_types.change_personal_email_ticket.uuid",
            spec=["uuid4"],
        )  # noqa
        UUIDMock.uuid4.return_value = "UUID-token"

        expected_ticket_data = {
            "Title": ChangeEmailPersonalConfiguration.subject,
            "QueueID": ChangeEmailPersonalConfiguration.queue_id,
            "State": ChangePersonalEmailTicket._get_state(self),
            "Type": ChangePersonalEmailTicket._get_type(self),
            "Priority": ChangePersonalEmailTicket._get_priority(self),
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": ChangeEmailPersonalConfiguration.subject,
            "Body": "-",
        }

        fields_dict = {
            "email": "fakeemail@email.coop",
        }

        ChangePersonalEmailTicket(
            username,
            customer_code,
            fields_dict,
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)

        expected_df_calls = [
            mocker.call(
                "ProcessManagementProcessID", "Process-b4243866849bc5c0c292f18100fad9d3"
            ),  # noqa
            mocker.call(
                "ProcessManagementActivityID",
                "Activity-8cc76400ded45e7b408f6d3e0267a2c6",
            ),  # noqa
            mocker.call("flagPartner", True),
            mocker.call("nouEmail", fields_dict["email"]),
            mocker.call("IDOV", UUIDMock.uuid4.return_value),
        ]
        for call in DynamicFieldMock.mock_calls:
            assert call in expected_df_calls

        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in expected_df_calls],
            attachments=None,
        )
