class GetTicketTitle:
    service_type_trans_dict = {
        "fiber": "fibra",
        "mobile": "mòbil",
        "adsl": "ADSL",
        "4G": "4G",
        "switchboard": "Centraleta Virtual",
    }

    def __init__(self, technology, order_id, service_type):
        self.technology = technology
        self.order_id = order_id
        self.service_type = service_type

    def build(self):
        if self.technology != "Mixta":
            title = "Ticket#{} - Només {}".format(
                self.order_id, self.service_type_trans_dict[self.service_type]
            )
        else:
            title = "Ticket#{} - {} mixta".format(
                self.order_id,
                self.service_type_trans_dict[self.service_type].capitalize(),
            )
        return title
