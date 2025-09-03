from otrs_somconnexio.services.base_get_ticket_by_number import BaseGetTicketByNumber


class GetMobileRelatedTickets(BaseGetTicketByNumber):
    def __init__(self, ticket_number, link_type="Normal"):
        super().__init__(ticket_number)
        self.link_type = link_type

    def run(self):
        super().run()
        return self.otrs_client.get_linked_tickets(self.ticket.tid, self.link_type)
