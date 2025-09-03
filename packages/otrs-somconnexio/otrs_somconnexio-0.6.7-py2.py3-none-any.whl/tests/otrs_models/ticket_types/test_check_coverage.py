from otrs_somconnexio.otrs_models.configurations.querys.check_coverage import (
    CheckCoverageCATConfiguration,
    CheckCoverageESConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.check_coverage_ticket import (
    CheckCoverageTicket,
)


class TestCaseCheckCoverage:
    fields_dict = {
        "name": "name",
        "surnames": "sunames",
        "email": "som@com.com",
        "phone": "642525377",
        "contact_lang": "ca_ES",
        "road_type": "carrer",
        "road_name": "melancolia",
        "road_number": "6",
        "block": "A",
        "doorway": "B",
        "floor": "3",
        "scale": "A",
        "door": "10",
        "other_information": "Altra info",
        "locality": "Alcobendas",
        "state": "Wisconsin",
        "zip_code": "46870",
        "language": "ca_ES",
    }

    def test_create_CAT(self, mocker):
        self._execute_and_assert_create(mocker, CheckCoverageCATConfiguration)

    def test_create_ES(self, mocker):
        self.fields_dict["language"] = "es_ES"
        self._execute_and_assert_create(mocker, CheckCoverageESConfiguration)

    def _execute_and_assert_create(self, mocker, config):
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
            mocker.call("nomSoci", self.fields_dict["name"]),
            mocker.call("cognom1", self.fields_dict["surnames"]),
            mocker.call("correuElectronic", self.fields_dict["email"]),
            mocker.call("telefonContacte", self.fields_dict["phone"]),
            mocker.call("idioma", self.fields_dict["contact_lang"]),
            mocker.call("tipusVia", self.fields_dict["road_type"]),
            mocker.call("nomVia", self.fields_dict["road_name"]),
            mocker.call("numero", self.fields_dict["road_number"]),
            mocker.call("bloc", self.fields_dict["block"]),
            mocker.call("portal", self.fields_dict["doorway"]),
            mocker.call("pis", self.fields_dict["floor"]),
            mocker.call("escala", self.fields_dict["scale"]),
            mocker.call("porta", self.fields_dict["door"]),
            mocker.call("altresCobertura", self.fields_dict["other_information"]),
            mocker.call("poblacioServei", self.fields_dict["locality"]),
            mocker.call("provinciaServei", self.fields_dict["state"]),
            mocker.call("CPservei", self.fields_dict["zip_code"]),
        ]

        CheckCoverageTicket(None, "customer", self.fields_dict, [], "").create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )
