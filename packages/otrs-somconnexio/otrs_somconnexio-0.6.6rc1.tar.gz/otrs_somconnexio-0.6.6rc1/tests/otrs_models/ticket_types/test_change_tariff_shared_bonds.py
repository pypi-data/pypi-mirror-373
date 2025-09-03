from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket import (
    ChangeTariffSharedBondTicket,
)


class TestCaseChangeTariffSharedBondTicket:
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
            "shared_bond_id": "123456",
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

        ticket = ChangeTariffSharedBondTicket(
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
                mocker.ANY,
            ],
            attachments=None,
        )
        DynamicFieldMock.assert_called_with(
            "IDAbonamentCompartit",
            fields_dict["shared_bond_id"],
        )
