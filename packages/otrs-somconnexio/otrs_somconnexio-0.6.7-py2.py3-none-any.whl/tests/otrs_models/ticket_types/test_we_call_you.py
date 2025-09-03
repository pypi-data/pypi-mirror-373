from otrs_somconnexio.otrs_models.configurations.querys.we_call_you import (
    WeCallYouCATConfiguration,
    WeCallYouCompanyCATConfiguration,
    WeCallYouCompanyESConfiguration,
    WeCallYouESConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.we_call_you_ticket import WeCallYouTicket


class TestCaseWeCallYou:
    fields_dict = {
        "name": "name surname",
        "schedule": "12h-14h",
        "phone": "642 525 377",
        "reason": "call me baby",
        "language": "ca_ES",
        "is_company": False,
        "referral": "referral",
        "email": "email.coop",
    }

    def test_create_CAT(self, mocker):
        self._execute_and_assert_create(
            mocker, WeCallYouCATConfiguration, self.fields_dict
        )

    def test_create_ES(self, mocker):
        dict = {**self.fields_dict}
        dict["language"] = "es_ES"
        self._execute_and_assert_create(mocker, WeCallYouESConfiguration, dict)

    def test_create_company_CAT(self, mocker):
        dict = {**self.fields_dict}
        dict["is_company"] = True
        dict["company_size"] = "1"
        self._execute_and_assert_create(
            mocker, WeCallYouCompanyCATConfiguration, dict, True
        )

    def test_create_company_ES(self, mocker):
        dict = {**self.fields_dict}
        dict["language"] = "es_ES"
        dict["is_company"] = True
        dict["company_size"] = "1"
        self._execute_and_assert_create(
            mocker, WeCallYouCompanyESConfiguration, dict, True
        )

    def _execute_and_assert_create(self, mocker, config, dict, is_company=False):
        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.OTRSClient",
            return_value=mocker.Mock(),
        )
        TicketMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Ticket",
            return_value=mocker.Mock(),
        )
        DynamicFieldMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.DynamicField",
            return_value=mocker.Mock(),
        )
        ArticleMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Article",
            return_value=mocker.Mock(),
        )

        expected_ticket_data = {
            "Title": config.subject,
            "QueueID": config.queue_id,
            "State": config.state,
            "Type": config.type,
            "Priority": config.priority,
            "CustomerUser": "customer",
            "CustomerID": "customer",
            "Service": False,
        }
        expected_article_data = {
            "Subject": config.subject,
            "Body": "-",
        }
        calls = [
            mocker.call("ProcessManagementProcessID", config.process_id),
            mocker.call(
                "ProcessManagementActivityID",
                config.activity_id,
            ),
            mocker.call("personaContacte", dict["name"]),
            mocker.call("horariTrucada", dict["schedule"]),
            mocker.call("telefonContacte", "642525377"),
            mocker.call("motiuTrucada", dict["reason"]),
            mocker.call("referral", dict["referral"]),
            mocker.call("rgpd", "1"),
            mocker.call("nouEmail", dict["email"]),
        ]
        if is_company:
            calls.append(mocker.call("midaEmpresa", dict["company_size"]))

        WeCallYouTicket(None, "customer", dict, [], "").create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )
