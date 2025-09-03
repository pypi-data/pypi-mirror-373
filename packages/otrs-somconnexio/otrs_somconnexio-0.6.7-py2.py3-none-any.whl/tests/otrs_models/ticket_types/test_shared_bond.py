from otrs_somconnexio.otrs_models.ticket_types.change_shared_bond_ticket import (
    ChangeSharedBondTicket,
)
from otrs_somconnexio.otrs_models.configurations.changes.change_shared_bond import (
    ChangeSharedBondTicketConfiguration,
)


class TestCaseChangeSharedBondTicket:
    def test_create(self, mocker):
        username = "7456787G"
        customer_code = "1234"
        configuration = ChangeSharedBondTicketConfiguration

        expected_ticket_data = {
            "Title": "Sol·licitud Canvi d'abonament compartit oficina virtual",
            "QueueID": configuration.queue_id,
            "State": configuration.state,
            "Type": configuration.type,
            "Priority": configuration.priority,
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": "Sol·licitud Canvi d'abonament compartit oficina virtual",
            "Body": "-",
        }

        fields_dict = {
            "phone_number": "666666666",
            "new_product_code": "BBBBBB",
            "new_shared_bond": "AAAA",
            "fiber_linked": "27722",
        }

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

        ticket = ChangeSharedBondTicket(username, customer_code, fields_dict).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call("ProcessManagementProcessID", configuration.process_id),
            mocker.call("ProcessManagementActivityID", configuration.activity_id),
            mocker.call("liniaMobil", fields_dict["phone_number"]),
            mocker.call("productMobil", fields_dict["new_product_code"]),
            mocker.call("IDAbonamentCompartit", fields_dict["new_shared_bond"]),
            mocker.call("OdooContractRefRelacionat", fields_dict["fiber_linked"]),
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
