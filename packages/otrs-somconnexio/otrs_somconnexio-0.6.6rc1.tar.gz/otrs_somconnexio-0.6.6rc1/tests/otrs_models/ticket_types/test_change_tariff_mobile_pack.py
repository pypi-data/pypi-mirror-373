from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket import (
    ChangeTariffMobilePackTicket,
)
from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket_mobile_pack import (
    ChangeTariffTicketMobilePack,
)


class TestCaseChangeTariffTicketMobilePack:
    def test_create(self, mocker):
        username = "7456787G"
        customer_code = "1234"
        ticket_creator_id = "1"
        ticket_id = "2"

        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket_mobile_pack.OTRSClient",
            return_value=mocker.Mock(),
        )

        ticket_mock = mocker.Mock(spec=["create"])
        ticket_mock.create.return_value = mocker.Mock(spec=["id"])
        ticket_mock.create.return_value.id = ticket_id
        ticket_creator_mock = mocker.Mock(spec=["create"])
        ticket_creator_mock.create.return_value = mocker.Mock(spec=["id"])
        ticket_creator_mock.create.return_value.id = ticket_creator_id

        def side_effect(uname, customer_c, fields, override):
            if fields.get("pack_creator"):
                return ticket_creator_mock
            else:
                return ticket_mock

        ChangeTariffMobilePackTicketMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket_mobile_pack.ChangeTariffMobilePackTicket",
            side_effect=side_effect,
        )

        fields_dict = {
            "contracts": [
                {
                    "phone_number": "666666666",
                    "current_product_code": "CURRENT_PRODUCT_CODE",
                    "subscription_email": "fakeemail@email.coop",
                },
                {
                    "phone_number": "777777777",
                    "current_product_code": "CURRENT_PRODUCT_CODE",
                    "subscription_email": "fakeemail@email.coop",
                },
            ],
            "phone_number": "666666666",
            "new_product_code": "NEW_PRODUCT_CODE",
            "effective_date": "tomorrow",
            "fiber_linked": "28",
            "language": "ca_ES",
            "send_notification": True,
        }

        ChangeTariffTicketMobilePack(username, customer_code, fields_dict).create()

        assert ChangeTariffMobilePackTicketMock.call_count == 2
        ticket_mock.create.assert_called_once_with()
        ticket_creator_mock.create.assert_called_once_with()
        OTRSClientMock.return_value.link_tickets.assert_called_once_with(
            ticket_creator_id,
            ticket_id,
            link_type="ParentChild",
        )

    def test_update(self, mocker):
        username = "7456787G"
        customer_code = "1234"
        ticket_id = "2"
        article = "article"
        dynamic_fields = "dynamic_fields"
        state = "state"
        ChangeTariffMobilePackTicketMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket_mobile_pack.ChangeTariffMobilePackTicket",
            return_value=mocker.Mock(spec=["update"]),
        )
        ChangeTariffTicketMobilePack(username, customer_code, {}).update(
            ticket_id, article, dynamic_fields, state
        )

        ChangeTariffMobilePackTicketMock.assert_called_once_with(
            username, customer_code, {}
        )
        ChangeTariffMobilePackTicketMock.return_value.update.assert_called_once_with(
            ticket_id, article, dynamic_fields, state
        )


class TestCaseChangeTariffMobilePackTicket:
    def test_create(self, mocker):
        username = "7456787G"
        customer_code = "1234"
        fields_dict = {
            "phone_number": "777777777",
            "current_product_code": "CURRENT_PRODUCT_CODE",
            "subscription_email": "fakeemail@email.coop",
            "new_product_code": "NEW_PRODUCT_CODE",
            "effective_date": "tomorrow",
            "fiber_linked": "28",
            "language": "ca_ES",
            "send_notification": True,
            "pack_creator": True,
        }

        ticket_mock = mocker.Mock(spec=["id"])
        ticket_mock.id = "11223344"
        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.OTRSClient",
            return_value=mocker.Mock(),
        )
        OTRSClientMock.return_value.create_otrs_process_ticket.return_value = (
            ticket_mock
        )
        DynamicFieldMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.DynamicField",
        )

        ticket = ChangeTariffMobilePackTicket(
            username, customer_code, fields_dict
        ).create()

        assert ticket.id == ticket_mock.id
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(
            mocker.ANY,
            article=mocker.ANY,
            dynamic_fields=[
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
                mocker.ANY,
            ],
            attachments=None,
        )
        DynamicFieldMock.assert_called_with(
            "creadorAbonament",
            True,
        )
