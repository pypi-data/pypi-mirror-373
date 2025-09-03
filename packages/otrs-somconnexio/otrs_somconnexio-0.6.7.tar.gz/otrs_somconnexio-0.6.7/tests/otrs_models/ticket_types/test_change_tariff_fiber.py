from otrs_somconnexio.otrs_models.configurations.changes.change_tariff_fiber import (
    ChangeTariffTicketFiberConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.change_tariff_fiber_ticket import (
    ChangeTariffTicketFiber,
)

username = "7456787G"
customer_code = "1234"


class TestCaseChangeTariffFiberTicket:
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
            "Title": ChangeTariffTicketFiberConfiguration.subject,
            "QueueID": ChangeTariffTicketFiberConfiguration.queue_id,
            "State": ChangeTariffTicketFiber._get_state(self),
            "Type": ChangeTariffTicketFiber._get_type(self),
            "Priority": ChangeTariffTicketFiber._get_priority(self),
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": ChangeTariffTicketFiberConfiguration.subject,
            "Body": "-",
        }

        fields_dict = {
            "ref_contract": "1256",
            "landline_number": "969999999",
            "service_address": "Carrer",
            "service_city": "Ciutat",
            "service_zip": "ZIPCODE",
            "service_state": "State",
            "effective_date": "1931-04-14",
            "previous_service": ChangeTariffTicketFiberConfiguration.code_fiber_100_landline,
        }

        ChangeTariffTicketFiber(
            username,
            customer_code,
            fields_dict,
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call(
                "ProcessManagementProcessID",
                ChangeTariffTicketFiberConfiguration.process_id,
            ),
            mocker.call(
                "ProcessManagementActivityID",
                ChangeTariffTicketFiberConfiguration.activity_id,
            ),
            mocker.call("refOdooContract", "1256"),
            mocker.call("telefonFixVell", "969999999"),
            mocker.call("direccioServei", "Carrer"),
            mocker.call("poblacioServei", "Ciutat"),
            mocker.call("CPservei", "ZIPCODE"),
            mocker.call("provinciaServei", "State"),
            mocker.call("serveiPrevi", "Fibra"),
            mocker.call(
                "productBA", ChangeTariffTicketFiberConfiguration.code_fiber_100
            ),
            mocker.call("dataExecucioCanviTarifa", "1931-04-14"),
            mocker.call("TecDelServei", "Fibra"),
        ]
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )

    def test_create_300(self, mocker):
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
            "Title": ChangeTariffTicketFiberConfiguration.subject,
            "QueueID": ChangeTariffTicketFiberConfiguration.queue_id,
            "State": ChangeTariffTicketFiber._get_state(self),
            "Type": ChangeTariffTicketFiber._get_type(self),
            "Priority": ChangeTariffTicketFiber._get_priority(self),
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": ChangeTariffTicketFiberConfiguration.subject,
            "Body": "-",
        }

        fields_dict = {
            "ref_contract": "1256",
            "landline_number": "969999999",
            "service_address": "Carrer",
            "service_city": "Ciutat",
            "service_zip": "ZIPCODE",
            "service_state": "State",
            "effective_date": "1931-04-14",
            "previous_service": "other_service",
        }

        ChangeTariffTicketFiber(
            username,
            customer_code,
            fields_dict,
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call(
                "ProcessManagementProcessID",
                ChangeTariffTicketFiberConfiguration.process_id,
            ),
            mocker.call(
                "ProcessManagementActivityID",
                ChangeTariffTicketFiberConfiguration.activity_id,
            ),
            mocker.call("refOdooContract", "1256"),
            mocker.call("telefonFixVell", "969999999"),
            mocker.call("direccioServei", "Carrer"),
            mocker.call("poblacioServei", "Ciutat"),
            mocker.call("CPservei", "ZIPCODE"),
            mocker.call("provinciaServei", "State"),
            mocker.call("serveiPrevi", "Fibra"),
            mocker.call(
                "productBA", ChangeTariffTicketFiberConfiguration.code_fiber_300
            ),
            mocker.call("dataExecucioCanviTarifa", "1931-04-14"),
            mocker.call("TecDelServei", "Fibra"),
        ]
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )
