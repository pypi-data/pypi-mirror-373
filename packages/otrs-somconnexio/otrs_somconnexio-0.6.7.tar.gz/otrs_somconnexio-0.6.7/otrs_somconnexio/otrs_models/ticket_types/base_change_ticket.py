import uuid
from otrs_somconnexio.otrs_models.ticket_types.base_customer_ticket import (
    BaseCustomerTicket,
)


class BaseChangeTicket(BaseCustomerTicket):
    def update(self, ticket_id):
        super().update(
            ticket_id,
        )

    def _new_value(self):
        return self.fields["new_value"]

    def _get_attribute_dynamic_field_name(self):
        raise NotImplementedError(
            "ChangeTickets must implement _get_attribute_dynamic_field_name"
        )

    def _get_dynamic_fields(self):
        result = {
            "IDOV": str(uuid.uuid4()),
            "idioma": self.fields["language"],
            "refOdooContract": ";".join(self.fields["selected_subscriptions"]),
        }

        result[self._get_attribute_dynamic_field_name()] = self._new_value()

        return result

    def _get_update_dynamic_fields(self):
        return {"enviatOdooOV": True}
