import pytest
from otrs_somconnexio.otrs_models.configurations.changes.change_email import (
    ChangeEmailContractsConfiguration,
    ChangeEmailPersonalConfiguration,
)
from otrs_somconnexio.otrs_models.configurations.changes.change_iban import (
    ChangeIbanTicketConfiguration,
)

from otrs_somconnexio.services.change_to_confirm_ticket import ChangeToConfirmTicket


class TestChangeToConfirmTicket:
    TOKEN = 593086396372

    def _execute_and_assert(self, mocker, queue_id):
        TICKET_ID = 1234
        ticket_OTRS_fixture = mocker.Mock(
            spec=[
                "fields",
                "field_get",
            ]
        )

        def field_get(f_name):
            return ticket_OTRS_fixture.fields.get(f_name)

        ticket_OTRS_fixture.fields = {"QueueID": queue_id, "TicketID": TICKET_ID}
        ticket_OTRS_fixture.field_get = field_get

        ChangeConfirmTicketInstance = ChangeToConfirmTicket()

        ticket_searched_fixture = [TICKET_ID]

        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.OTRSClient",
            return_value=mocker.Mock(),
        )
        DynamicFieldMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.DynamicField",
            return_value=mocker.Mock(),
        )

        OTRSClientMock.return_value.client.ticket_search.return_value = (
            ticket_searched_fixture
        )
        OTRSClientMock.return_value.client.ticket_get_by_id.return_value = (
            ticket_OTRS_fixture
        )
  
        ChangeConfirmTicketInstance.confirm(self.TOKEN)

        DynamicFieldMock.assert_has_calls(
            [
                mocker.call("IDOV", search_patterns=self.TOKEN),
                mocker.call("enviatOdooOV", True),
            ]
        )
        OTRSClientMock.return_value.client.ticket_search.assert_called_once_with(
            dynamic_fields=[DynamicFieldMock.return_value]
        )
        OTRSClientMock.return_value.client.ticket_get_by_id.assert_called_once_with(
            ticket_id=TICKET_ID
        )
        OTRSClientMock.return_value.client.ticket_update.assert_called_once_with(
            TICKET_ID, article=None,  dynamic_fields=[DynamicFieldMock.return_value], State=None, attachments=None
        )

    def test_confirm_change_iban(self, mocker):
        self._execute_and_assert(mocker, ChangeIbanTicketConfiguration.queue_id)

    def test_confirm_change_contract_email(self, mocker):
        self._execute_and_assert(mocker, ChangeEmailContractsConfiguration.queue_id)

    def test_confirm_change_user_email(self, mocker):
        self._execute_and_assert(mocker, ChangeEmailPersonalConfiguration.queue_id)

    def test_confirm_change_ticket_bad_queue(self, mocker):
        with pytest.raises(Exception):
            self._execute_and_assert(mocker, 0)
