from otrs_somconnexio.otrs_models.configurations.changes.change_owner import (
    ChangeOwnerPackTicketConfiguration,
    ChangeOwnerTicketConfiguration,
)
from otrs_somconnexio.otrs_models.ticket_types.base_change_ticket import (
    BaseChangeTicket,
)


class BaseChangeOwnerTicket(BaseChangeTicket):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        configuration,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(BaseChangeOwnerTicket, self).__init__(
            username,
            customer_code,
            fields_dict,
            override_ticket_ids,
            fallback_path,
        )
        self.configuration = configuration()

    def _get_activity_id(self):
        return self.configuration.activity_id

    def _get_process_id(self):
        return self.configuration.process_id

    def _get_queue_id(self):
        return self.configuration.queue_id

    def _get_subject(self):
        return self.configuration.subject

    def _get_attribute_dynamic_field_name(self):
        return "nouEmail"

    def _get_docs(self):
        return [self._get_attachment_content(doc) for doc in self.fields["docs"]]

    def _get_body(self):
        return self.configuration.body

    def _get_update_dynamic_fields(self):
        dynamic_fields = super()._get_update_dynamic_fields()
        dynamic_fields.update(
            [
                # common fields
                ("situacioNovaTitular", self.fields["role_new_owner"]),
                ("definicioNovaTitular", self.fields["legal_entity"]),
                ("nomSoci", self.fields["name_new_owner"]),
                ("NIFNIENovaTitular", self.fields["vat_new_owner"]),
                ("correuElectronic", self.fields["email_new_owner"]),
                ("IBAN", self.fields["iban_new_owner"]),
                # new user fields
                ("idiomaNovaTitular", self.fields.get("lang")),
                ("telefonContacte", self.fields.get("phone_contact")),
                ("adrecaNovaTitular", self.fields.get("address_street_contact")),
                ("localitatNovaTitular", self.fields.get("address_city_contact")),
                ("cpNovaTitular", self.fields.get("address_zip_code_contact")),
                ("codiProvinciaServei", self.fields.get("address_state_contact")),
                # new partner fields
                ("IBANaportacio", self.fields.get("iban_new_partner")),
                ("fraccionarPagament", self.fields.get("pays_in_ten_terms")),
                # new sponsorship fields
                ("NIFNIESoci", self.fields.get("sponsor_vat")),
                ("codiApadrinament", self.fields.get("sponsor_code")),
            ]
        )
        return dynamic_fields

    def _get_update_article_content(self):
        return {
            "Subject": self.configuration.update_subject,
            "Body": self.configuration.update_body,
        }

    def _get_update_docs(self):
        return [
            self._get_attachment_content(doc) for doc in self.fields["next_owner_docs"]
        ]

    def _get_attachment_content(self, doc):
        return {
            "Content": doc["content"],
            "ContentType": doc["file_type"],
            "Filename": doc["file_name"],
        }


class ChangeOwnerTicket(BaseChangeOwnerTicket):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(ChangeOwnerTicket, self).__init__(
            username,
            customer_code,
            fields_dict,
            ChangeOwnerTicketConfiguration,
            override_ticket_ids,
            fallback_path,
        )


class ChangeOwnerPackTicket(BaseChangeOwnerTicket):
    def __init__(
        self,
        username,
        customer_code,
        fields_dict,
        override_ticket_ids=[],
        fallback_path="/tmp/tickets/",
    ):
        super(ChangeOwnerPackTicket, self).__init__(
            username,
            customer_code,
            fields_dict,
            ChangeOwnerPackTicketConfiguration,
            override_ticket_ids,
            fallback_path,
        )
