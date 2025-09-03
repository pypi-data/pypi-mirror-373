from otrs_somconnexio.otrs_models.configurations.changes.change_tariff_adsl import (
    ChangeTariffTicketAdslLandlineConfig,
)
from otrs_somconnexio.otrs_models.ticket_types.change_tariff_adsl_landline_ticket import (
    ChangeTariffLandLineADSL,
)


username = "7456787G"
customer_code = "1234"


class TestCaseChangeTariffAdslLandlineTicket:
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
            "Title": ChangeTariffTicketAdslLandlineConfig.subject,
            "QueueID": ChangeTariffTicketAdslLandlineConfig.queue_id,
            "State": ChangeTariffLandLineADSL._get_state(self),
            "Type": ChangeTariffLandLineADSL._get_type(self),
            "Priority": ChangeTariffLandLineADSL._get_priority(self),
            "CustomerUser": customer_code,
            "CustomerID": customer_code,
            "Service": False,
        }
        expected_article_data = {
            "Subject": ChangeTariffTicketAdslLandlineConfig.subject,
            "Body": "-",
        }

        fields_dict = {
            "ref_contract": "1256",
            "landline_number": "969999999",
            "service_address": "Carrer",
            "service_city": "Ciutat",
            "service_zip": "ZIPCODE",
            "service_state": "State",
            "name": "Name",
            "sur_name": "Surname",
            "last_name": "Lastname",
            "complete_name": "CompleteName",
            "vat_number": "VAT",
            "iban": "IBAN",
            "customer_email": "customerEmail",
            "service_state_code": "stateCode",
            "customer_phone": "969999992",
            "is_fiber_landline": True,
            "previous_technology": "ADSL",
        }

        ChangeTariffLandLineADSL(
            username,
            customer_code,
            fields_dict,
        ).create()

        TicketMock.assert_called_once_with(expected_ticket_data)
        ArticleMock.assert_called_once_with(expected_article_data)
        calls = [
            mocker.call(
                "ProcessManagementProcessID",
                ChangeTariffTicketAdslLandlineConfig.process_id,
            ),
            mocker.call(
                "ProcessManagementActivityID",
                ChangeTariffTicketAdslLandlineConfig.activity_id,
            ),
            mocker.call("refOdooContract", "1256"),
            mocker.call("telefonFixVell", "969999999"),
            mocker.call("direccioServei", "Carrer"),
            mocker.call("poblacioServei", "Ciutat"),
            mocker.call("CPservei", "ZIPCODE"),
            mocker.call("provinciaServei", "State"),
            mocker.call("serveiPrevi", "ADSL"),
            mocker.call("productBA", ChangeTariffTicketAdslLandlineConfig.code_fiber),
            mocker.call("nomSoci", "Name"),
            mocker.call("titular", "Name"),
            mocker.call("cognom1", "Surname Lastname"),
            mocker.call("cognom1Titular", "Surname Lastname"),
            mocker.call("nomCognomSociAntic", "CompleteName"),
            mocker.call("NIFNIESoci", "VAT"),
            mocker.call("NIFNIEtitular", "VAT"),
            mocker.call("IBAN", "IBAN"),
            mocker.call("telefonFixAntic", "969999999"),
            mocker.call("IDContracte", "-"),
            mocker.call("correuElectronic", "customerEmail"),
            mocker.call("direccioServeiAntic", "Carrer - ZIPCODE Ciutat State"),
            mocker.call("codiProvinciaServei", "stateCode"),
            mocker.call("telefonContacte", "969999992"),
            mocker.call("canviUbicacioMateixTitular", "yes"),
            mocker.call("TecDelServei", "ADSL"),
        ]
        DynamicFieldMock.assert_has_calls(calls)
        OTRSClientMock.return_value.create_otrs_process_ticket.assert_called_once_with(  # noqa
            TicketMock.return_value,
            article=ArticleMock.return_value,
            dynamic_fields=[mocker.ANY for call in calls],
            attachments=None,
        )
