from otrs_somconnexio.otrs_models.ticket_types.base_change_ticket import (
    BaseChangeTicket,
)
from otrs_somconnexio.otrs_models.configurations.changes.change_email import (
    ChangeEmailContractsConfiguration,
    ChangeEmailPersonalConfiguration,
)
from otrs_somconnexio.otrs_models.configurations.changes.change_iban import (
    ChangeIbanTicketConfiguration,
)


class ChangeToConfirmTicket(BaseChangeTicket):
    """
    Set DF enviatOdooOV to True to OTRS change email/iban tickets.
    """

    QUEUES_IDS_TO_APPLIE_CHANGE = [
        ChangeIbanTicketConfiguration.queue_id,
        ChangeEmailContractsConfiguration.queue_id,
        ChangeEmailPersonalConfiguration.queue_id,
    ]

    def __init__(self):
        super(ChangeToConfirmTicket, self).__init__(
            username=None, customer_code=None, fields_dict=None
        )

    def confirm(self, token):
        ticket = self.get_by_IDOV(token)
        if ticket.field_get("QueueID") in self.QUEUES_IDS_TO_APPLIE_CHANGE:
            self.update(
                ticket.field_get("TicketID"),
            )
        else:
            raise Exception(
                """
Change confirmed for ticket in unexpected queue.
- Ticket ID: {ticket_id}
- QueueID: {queue_id}
                """.format(
                    ticket_id=ticket.field_get("TicketID"),
                    queue_id=ticket.field_get("QueueID"),
                )
            )
