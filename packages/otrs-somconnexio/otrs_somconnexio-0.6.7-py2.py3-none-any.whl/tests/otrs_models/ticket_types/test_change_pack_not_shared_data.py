from otrs_somconnexio.otrs_models.configurations.changes.change_pack import (
    ChangePackNotSharedDataTicketConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.change_pack_not_shared_data import (
    ChangePackNotSharedDataTicket,
)

username = "7456787G"
customer_code = "1234"


class TestCaseChangePackNotSharedDataTicket:
    def test_create(self, mocker):
        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.OTRSClient",
            return_value=mocker.Mock(),
        )
        TicketMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Ticket",
            return_value=mocker.Mock(),
        )
        ArticleMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Article",
            return_value=mocker.Mock(),
        )
        DynamicFieldMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.DynamicField",
            return_value=mocker.Mock(),
        )

        expected_ticket_data = {
            "Title": ChangePackNotSharedDataTicketConfiguration.subject,
            "QueueID": ChangePackNotSharedDataTicketConfiguration.queue_id,
            "State": ChangePackNotSharedDataTicket._get_state(self),
            "Type": ChangePackNotSharedDataTicket._get_type(self),
            "Priority": ChangePackNotSharedDataTicket._get_priority(self),
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": ChangePackNotSharedDataTicketConfiguration.service,
        }
        expected_article_data = {
            "Subject": ChangePackNotSharedDataTicketConfiguration.subject,
            "Body": "-",
        }

        fields_dict = {
            "selected_subscriptions": ["111", "222"],
            "fiber_without_landline": True,
        }

        ChangePackNotSharedDataTicket(
            username,
            customer_code,
            fields_dict,
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call(
                "ProcessManagementProcessID",
                ChangePackNotSharedDataTicketConfiguration.process_id,
            ),
            mocker.call(
                "ProcessManagementActivityID",
                ChangePackNotSharedDataTicketConfiguration.activity_id,
            ),
            mocker.call("refOdooContract", "111;222"),
            mocker.call("fibraSenseFix", "1"),
        ]
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )
