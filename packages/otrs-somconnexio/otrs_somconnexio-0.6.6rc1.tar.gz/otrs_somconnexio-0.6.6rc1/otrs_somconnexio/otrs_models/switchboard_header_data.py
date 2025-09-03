class SwitchboardHeaderData:
    service_type = "header_switchboard"

    def __init__(
        self,
        order_id,
        email,
        contact_phone,
        sales_team,
        technology,
        notes="",
    ):
        self.order_id = order_id
        self.email = email
        self.contact_phone = contact_phone
        self.sales_team = sales_team
        self.technology = technology
        self.notes = notes
