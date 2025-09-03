class SwitchboardData:
    service_type = "switchboard"

    def __init__(
        self,
        order_id,
        iban,
        email,
        contact_phone,
        product,
        technology,
        sales_team,
        type,
        landline,
        mobile_phone_number,
        icc,
        has_sim,
        extension,
        agent_name,
        agent_email,
        previous_owner_vat,
        previous_owner_name,
        previous_owner_surname,
        shipment_address,
        shipment_city,
        shipment_zip,
        shipment_subdivision,
        additional_products,
        activation_notes="",
        notes="",
    ):
        self.order_id = order_id
        self.iban = iban
        self.email = email
        self.contact_phone = contact_phone
        self.product = product
        self.technology = technology
        self.sales_team = sales_team
        self.type = type
        self.landline = landline
        self.mobile_phone_number = mobile_phone_number
        self.icc = icc
        self.has_sim = has_sim
        self.extension = extension
        self.agent_name = agent_name
        self.agent_email = agent_email
        self.previous_owner_vat = previous_owner_vat
        self.previous_owner_name = previous_owner_name
        self.previous_owner_surname = previous_owner_surname
        self.shipment_address = shipment_address
        self.shipment_city = shipment_city
        self.shipment_zip = shipment_zip
        self.shipment_subdivision = shipment_subdivision
        self.additional_products = additional_products
        self.activation_notes = activation_notes
        self.notes = notes
