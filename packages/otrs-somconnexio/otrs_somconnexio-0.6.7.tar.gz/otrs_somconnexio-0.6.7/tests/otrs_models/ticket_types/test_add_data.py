


from otrs_somconnexio.otrs_models.configurations.changes.add_data import AddDataTicketConfiguration, AddDataTicketRequestedConfiguration
from otrs_somconnexio.otrs_models.ticket_types.add_data_ticket import AddDataTicket

username = "7456787G"
customer_code = "1234"

class TestCaseAddDataTicket:
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
            "Title": AddDataTicketConfiguration.subject,
            "QueueID": AddDataTicketConfiguration.queue_id,
            "State": AddDataTicket._get_state(self),
            "Type": AddDataTicket._get_type(self),
            "Priority": AddDataTicket._get_priority(self),
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": AddDataTicketConfiguration.subject,
            "Body": "-",
        }

        fields_dict = {
            "phone_number": "666666666",
            "new_product_code": "PRODUCT_CODE",
            "subscription_email": "fakeemail@email.coop",
            "language": "ca_ES",
        }

        AddDataTicket(
            username,
            customer_code,
            fields_dict,
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call(
                "ProcessManagementProcessID", AddDataTicketConfiguration.process_id
            ),
            mocker.call(
                "ProcessManagementActivityID",
                AddDataTicketConfiguration.activity_id,
            ),
            mocker.call("liniaMobil", "666666666"),
            mocker.call("productAbonamentDadesAddicionals", "PRODUCT_CODE"),
            # TODO: Why are we using correuElectronic in this ticket?
            mocker.call("correuElectronic", "fakeemail@email.coop"),
            mocker.call("idioma", "ca_ES"),
        ]
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )
