from otrs_somconnexio.otrs_models.configurations.changes.change_owner import (
    ChangeOwnerConfiguration,
    ChangeOwnerTicketConfiguration,
    ChangeOwnerPackTicketConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.change_owner_ticket import (
    ChangeOwnerTicket,
    ChangeOwnerPackTicket,
)


class TestCaseChangeOwnerTicket:
    fields_dict_create = {
        "new_value": "email@email",
        "selected_subscriptions": ["123"],
        "language": "ca_ES",
        "scope": "some",
        "docs": [{"content": "content", "file_type": "type", "file_name": "name"}],
    }

    common_fields_dict_update = {
        "role_new_owner": "role",
        "legal_entity": "entity",
        "name_new_owner": "name",
        "vat_new_owner": "vat",
        "email_new_owner": "email",
        "iban_new_owner": "iban",
        "next_owner_docs": [
            {"content": "content", "file_type": "type", "file_name": "name"}
        ],
    }

    new_user_fields_dict_update = {
        "lang": "lang",
        "phone_contact": "666666666",
        "address_street_contact": "carrer",
        "address_city_contact": "ciutat",
        "address_zip_code_contact": "46870",
        "address_state_contact": "AL",
        "is_new_user": True,
    }

    def _get_common_calls_update(self, mocker):
        return [
            mocker.call("enviatOdooOV", True),
            mocker.call("situacioNovaTitular", "role"),
            mocker.call("definicioNovaTitular", "entity"),
            mocker.call("nomSoci", "name"),
            mocker.call("NIFNIENovaTitular", "vat"),
            mocker.call("correuElectronic", "email"),
            mocker.call("IBAN", "iban"),
        ]

    def _get_new_user_calls_update(self, mocker):
        return [
            mocker.call("idiomaNovaTitular", "lang"),
            mocker.call("telefonContacte", "666666666"),
            mocker.call("adrecaNovaTitular", "carrer"),
            mocker.call("localitatNovaTitular", "ciutat"),
            mocker.call("cpNovaTitular", "46870"),
            mocker.call("codiProvinciaServei", "AL"),
        ]

    def _get_calls_create(
        self,
        mocker,
        config=ChangeOwnerTicketConfiguration,
    ):
        return [
            mocker.call("ProcessManagementProcessID", config.process_id),
            mocker.call(
                "ProcessManagementActivityID",
                config.activity_id,
            ),
            mocker.call("IDOV", "UUID-token"),
            mocker.call("idioma", "ca_ES"),
            mocker.call("nouEmail", "email@email"),
        ]

    def _execute_and_assert_create(
        self,
        mocker,
        fields_dict,
        calls,
        config=ChangeOwnerTicketConfiguration,
        target=ChangeOwnerTicket,
    ):
        username = "7456787G"
        customer_code = "1234"
        expected_article_data = {
            "Subject": config.subject,
            "Body": config.body,
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
        AttachmentMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Attachment",
            return_value=mocker.Mock(),
        )
        DynamicFieldMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.DynamicField",
            return_value=mocker.Mock(),
        )
        UUIDMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_change_ticket.uuid",
            spec=["uuid4"],
        )
        UUIDMock.uuid4.return_value = "UUID-token"

        expected_ticket_data = {
            "Title": config.subject,
            "QueueID": config.queue_id,
            "State": config.state,
            "Type": config.type,
            "Priority": config.priority,
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }

        ticket = target(username, customer_code, fields_dict).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        AttachmentMock.assert_called_once_with(
            {"Content": "content", "ContentType": "type", "Filename": "name"}
        )
        DynamicFieldMock.assert_has_calls(calls)

        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=[AttachmentMock.return_value],
        )
        assert ticket.id == "1"

    def _execute_and_assert_update(
        self, mocker, fields_dict, calls, target=ChangeOwnerTicket
    ):
        ticket_id = "1234"
        username = None
        customer_code = None
        expected_article_data = {
            "Subject": ChangeOwnerConfiguration.update_subject,
            "Body": ChangeOwnerConfiguration.update_body,
        }

        OTRSClientMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.OTRSClient",
            return_value=mocker.Mock(),
        )
        DynamicFieldMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.DynamicField",
            return_value=mocker.Mock(),
        )
        AttachmentMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Attachment",
            return_value=mocker.Mock(),
        )
        ArticleMock = mocker.patch(
            "otrs_somconnexio.otrs_models.ticket_types.base_ticket.Article",
            return_value=mocker.Mock(),
        )

        ticket = target(username, customer_code, fields_dict)
        ticket.update(ticket_id)

        AttachmentMock.assert_called_once_with(
            {"Content": "content", "ContentType": "type", "Filename": "name"}
        )
        ArticleMock.assert_called_once_with(expected_article_data)
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.client.ticket_update.assert_called_once_with(
            ticket_id,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            State=None,
            attachments=[AttachmentMock.return_value],
        )

    def test_create_some(self, mocker):
        fields_dict = self.fields_dict_create
        calls = self._get_calls_create(mocker)
        calls.insert(4, mocker.call("refOdooContract", "123"))

        self._execute_and_assert_create(mocker, fields_dict, calls)

    def test_create_pack(self, mocker):
        fields_dict = self.fields_dict_create
        calls = self._get_calls_create(mocker, ChangeOwnerPackTicketConfiguration)
        calls.insert(4, mocker.call("refOdooContract", "123"))

        self._execute_and_assert_create(
            mocker,
            fields_dict,
            calls,
            ChangeOwnerPackTicketConfiguration,
            ChangeOwnerPackTicket,
        )

    def test_create_all(self, mocker):
        fields_dict = self.fields_dict_create
        fields_dict["scope"] = "all"
        fields_dict["selected_subscriptions"] = ["123", "321"]
        calls = self._get_calls_create(mocker)
        calls.insert(4, mocker.call("refOdooContract", "123;321"))

        self._execute_and_assert_create(mocker, fields_dict, calls)

    def test_update_new_owner_already_user(self, mocker):
        fields_dict = self.common_fields_dict_update
        calls = self._get_common_calls_update(mocker)
        self._execute_and_assert_update(mocker, fields_dict, calls)

    def test_update_new_owner_new_user_partner(self, mocker):
        fields_dict = {
            **self.common_fields_dict_update,
            **self.new_user_fields_dict_update,
            **{
                "is_new_partner": True,
                "iban_new_partner": "iban",
                "pays_in_ten_terms": "0",
            },
        }
        calls = (
            self._get_common_calls_update(mocker)
            + self._get_new_user_calls_update(mocker)
            + [
                mocker.call("IBANaportacio", "iban"),
                mocker.call("fraccionarPagament", "0"),
            ]
        )
        self._execute_and_assert_update(mocker, fields_dict, calls)

    def test_update_new_owner_new_user_sponsorship(self, mocker):
        fields_dict = {
            **self.common_fields_dict_update,
            **self.new_user_fields_dict_update,
            **{
                "is_new_sponsorship": True,
                "sponsor_vat": "vat",
                "sponsor_code": "code",
            },
        }
        calls = (
            self._get_common_calls_update(mocker)
            + self._get_new_user_calls_update(mocker)
            + [
                mocker.call("NIFNIESoci", "vat"),
                mocker.call("codiApadrinament", "code"),
            ]
        )
        self._execute_and_assert_update(mocker, fields_dict, calls)

    def test_update_pack(self, mocker):
        fields_dict = self.common_fields_dict_update
        calls = self._get_common_calls_update(mocker)
        self._execute_and_assert_update(
            mocker, fields_dict, calls, target=ChangeOwnerPackTicket
        )
