from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket import (
    ChangeTariffTicket,
    ChangeTariffExceptionalTicket,
    ChangeTariffMobilePackTicket,
    ChangeTariffSharedBondTicket,
)
from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffTicketConfiguration,
    ChangeTariffExceptionalTicketConfiguration,
    ChangeTariffSharedBondTicketConfiguration,
)


class TestCaseChangeTariffTicket:
    def test_create(self, mocker):
        username = "7456787G"
        customer_code = "1234"

        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.OTRSClient",
            return_value=mocker.Mock(),
        )
        OTRSClientMock.return_value.create_otrs_process_ticket.return_value = (
            mocker.Mock(spec=["id"])
        )
        OTRSClientMock.return_value.create_otrs_process_ticket.return_value.id = "1"

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
            "Title": "Sol·licitud Canvi de tarifa oficina virtual",
            "QueueID": ChangeTariffTicketConfiguration.queue_id,
            "State": ChangeTariffTicketConfiguration.state,
            "Type": ChangeTariffTicketConfiguration.type,
            "Priority": ChangeTariffTicketConfiguration.priority,
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": "Sol·licitud Canvi de tarifa oficina virtual",
            "Body": "-",
        }

        fields_dict = {
            "phone_number": "666666666",
            "new_product_code": "NEW_PRODUCT_CODE",
            "current_product_code": "CURRENT_PRODUCT_CODE",
            "effective_date": "tomorrow",
            "fiber_linked": "",
            "subscription_email": "fakeemail@email.coop",
            "language": "ca_ES",
            "send_notification": False,
        }

        ticket = ChangeTariffTicket(username, customer_code, fields_dict).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call(
                "ProcessManagementProcessID", ChangeTariffTicketConfiguration.process_id
            ),
            mocker.call(
                "ProcessManagementActivityID",
                ChangeTariffTicketConfiguration.activity_id,
            ),
            mocker.call("renovaCanviTarifa", "0"),
            mocker.call("liniaMobil", "666666666"),
            mocker.call("productMobil", "NEW_PRODUCT_CODE"),
            mocker.call("tarifaAntiga", "CURRENT_PRODUCT_CODE"),
            mocker.call("dataExecucioCanviTarifa", "tomorrow"),
            mocker.call("correuElectronic", "fakeemail@email.coop"),
            mocker.call("idioma", "ca_ES"),
            mocker.call("enviarNotificacio", "0"),
            mocker.call("TecDelServei", "Mobil"),
        ]
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )
        assert ticket.id == "1"

    def test_create_with_override_tickets(self, mocker):
        username = "7456787G"
        customer_code = "1234"

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
            "Title": "Sol·licitud Canvi de tarifa oficina virtual",
            "QueueID": ChangeTariffTicketConfiguration.queue_id,
            "State": ChangeTariffTicketConfiguration.state,
            "Type": ChangeTariffTicketConfiguration.type,
            "Priority": ChangeTariffTicketConfiguration.priority,
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": "Sol·licitud Canvi de tarifa oficina virtual",
            "Body": "-",
        }

        fields_dict = {
            "phone_number": "666666666",
            "new_product_code": "NEW_PRODUCT_CODE",
            "current_product_code": "CURRENT_PRODUCT_CODE",
            "effective_date": "tomorrow",
            "fiber_linked": "",
            "subscription_email": "fakeemail@email.coop",
            "language": "es_ES",
        }

        ChangeTariffTicket(
            username, customer_code, fields_dict, override_ticket_ids=[1, 2]
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call(
                "ProcessManagementProcessID", ChangeTariffTicketConfiguration.process_id
            ),
            mocker.call(
                "ProcessManagementActivityID",
                ChangeTariffTicketConfiguration.activity_id,
            ),
            mocker.call("renovaCanviTarifa", "1"),
            mocker.call("liniaMobil", "666666666"),
            mocker.call("productMobil", "NEW_PRODUCT_CODE"),
            mocker.call("tarifaAntiga", "CURRENT_PRODUCT_CODE"),
            mocker.call("dataExecucioCanviTarifa", "tomorrow"),
            mocker.call("correuElectronic", "fakeemail@email.coop"),
            mocker.call("idioma", "es_ES"),
            mocker.call("enviarNotificacio", "1"),
            mocker.call("TecDelServei", "Mobil"),
        ]
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )


class TestCaseChangeTariffExceptionalTicket:
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
            "Title": "Sol·licitud Canvi de tarifa excepcional",
            "QueueID": ChangeTariffExceptionalTicketConfiguration.queue_id,
            "State": ChangeTariffExceptionalTicketConfiguration.state,
            "Type": ChangeTariffExceptionalTicketConfiguration.type,
            "Priority": ChangeTariffExceptionalTicketConfiguration.priority,
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": "Sol·licitud Canvi de tarifa excepcional",
            "Body": "-",
        }

        fields_dict = {
            "phone_number": "666666666",
            "new_product_code": "NEW_PRODUCT_CODE",
            "current_product_code": "CURRENT_PRODUCT_CODE",
            "effective_date": "tomorrow",
            "fiber_linked": "28",
            "subscription_email": "fakeemail@email.coop",
            "language": "ca_ES",
            "send_notification": True,
        }

        ChangeTariffExceptionalTicket(username, customer_code, fields_dict).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call(
                "ProcessManagementProcessID",
                ChangeTariffExceptionalTicketConfiguration.process_id,
            ),
            mocker.call(
                "ProcessManagementActivityID",
                ChangeTariffExceptionalTicketConfiguration.activity_id,
            ),
            mocker.call("renovaCanviTarifa", "0"),
            mocker.call("liniaMobil", "666666666"),
            mocker.call("productMobil", "NEW_PRODUCT_CODE"),
            mocker.call("tarifaAntiga", "CURRENT_PRODUCT_CODE"),
            mocker.call("dataExecucioCanviTarifa", "tomorrow"),
            mocker.call("OdooContractRefRelacionat", "28"),
            mocker.call("correuElectronic", "fakeemail@email.coop"),
            mocker.call("idioma", "ca_ES"),
            mocker.call("enviarNotificacio", "1"),
            mocker.call("TecDelServei", "Mobil"),
        ]
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )


class TestCaseChangeTariffMobilePackTicket:
    def test_create(self, mocker):
        username = "7456787G"
        customer_code = "1234"

        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.OTRSClient",
            return_value=mocker.Mock(),
        )
        OTRSClientMock.return_value.create_otrs_process_ticket.return_value = (
            mocker.Mock(spec=["id"])
        )
        OTRSClientMock.return_value.create_otrs_process_ticket.return_value.id = "1"

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
            "Title": "Sol·licitud canvi de tarifa pack apinyades",
            "QueueID": ChangeTariffTicketConfiguration.queue_id,
            "State": ChangeTariffTicketConfiguration.state,
            "Type": ChangeTariffTicketConfiguration.type,
            "Priority": ChangeTariffTicketConfiguration.priority,
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": "Sol·licitud canvi de tarifa pack apinyades",
            "Body": "-",
        }

        fields_dict = {
            "phone_number": "666666666",
            "new_product_code": "NEW_PRODUCT_CODE",
            "current_product_code": "CURRENT_PRODUCT_CODE",
            "effective_date": "tomorrow",
            "fiber_linked": "",
            "subscription_email": "fakeemail@email.coop",
            "language": "ca_ES",
            "send_notification": False,
        }

        ticket = ChangeTariffMobilePackTicket(
            username, customer_code, fields_dict
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call(
                "ProcessManagementProcessID",
                ChangeTariffTicketConfiguration.process_id,
            ),
            mocker.call(
                "ProcessManagementActivityID",
                ChangeTariffTicketConfiguration.activity_id,
            ),
            mocker.call("renovaCanviTarifa", "0"),
            mocker.call("liniaMobil", "666666666"),
            mocker.call("productMobil", "NEW_PRODUCT_CODE"),
            mocker.call("tarifaAntiga", "CURRENT_PRODUCT_CODE"),
            mocker.call("dataExecucioCanviTarifa", "tomorrow"),
            mocker.call("correuElectronic", "fakeemail@email.coop"),
            mocker.call("idioma", "ca_ES"),
            mocker.call("enviarNotificacio", "0"),
            mocker.call("TecDelServei", "Mobil"),
        ]

        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )
        assert ticket.id == "1"


class TestCaseChangeTariffSharedBondTicket:
    def test_create_with_shared_bond_id(self, mocker):
        username = "7456787G"
        customer_code = "1234"

        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.OTRSClient",
            return_value=mocker.Mock(),
        )
        OTRSClientMock.return_value.create_otrs_process_ticket.return_value = (
            mocker.Mock(spec=["id"])
        )
        OTRSClientMock.return_value.create_otrs_process_ticket.return_value.id = "1"

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
            "Title": "Sol·licitud canvi de tarifa pack amb dades compartides",
            "QueueID": ChangeTariffSharedBondTicketConfiguration.queue_id,
            "State": ChangeTariffSharedBondTicketConfiguration.state,
            "Type": ChangeTariffSharedBondTicketConfiguration.type,
            "Priority": ChangeTariffSharedBondTicketConfiguration.priority,
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": "Sol·licitud canvi de tarifa pack amb dades compartides",
            "Body": "-",
        }

        fields_dict = {
            "phone_number": "666666666",
            "new_product_code": "NEW_PRODUCT_CODE",
            "current_product_code": "CURRENT_PRODUCT_CODE",
            "effective_date": "tomorrow",
            "fiber_linked": "",
            "subscription_email": "fakeemail@email.coop",
            "language": "ca_ES",
            "send_notification": False,
            "shared_bond_id": "C03457456M",
        }

        ticket = ChangeTariffSharedBondTicket(
            username, customer_code, fields_dict
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call(
                "ProcessManagementProcessID",
                ChangeTariffSharedBondTicketConfiguration.process_id,
            ),
            mocker.call(
                "ProcessManagementActivityID",
                ChangeTariffSharedBondTicketConfiguration.activity_id,
            ),
            mocker.call("renovaCanviTarifa", "0"),
            mocker.call("liniaMobil", "666666666"),
            mocker.call("productMobil", "NEW_PRODUCT_CODE"),
            mocker.call("tarifaAntiga", "CURRENT_PRODUCT_CODE"),
            mocker.call("dataExecucioCanviTarifa", "tomorrow"),
            mocker.call("correuElectronic", "fakeemail@email.coop"),
            mocker.call("idioma", "ca_ES"),
            mocker.call("enviarNotificacio", "0"),
            mocker.call("TecDelServei", "Mobil"),
            mocker.call("IDAbonamentCompartit", "C03457456M"),
        ]

        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )
        assert ticket.id == "1"
