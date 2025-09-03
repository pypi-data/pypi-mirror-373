class MobileData:
    service_type = "mobile"

    def __init__(
        self,
        order_id,
        contact_phone,
        phone_number,
        iban,
        email,
        sc_icc,
        icc,
        has_sim,
        type,
        previous_owner_vat,
        previous_owner_name,
        previous_owner_surname,
        previous_provider,
        product,
        delivery_street,
        delivery_city,
        delivery_zip_code,
        delivery_state,
        technology,
        sim_delivery_tracking_code,
        sales_team,
        activation_notes="",
        notes="",
        is_grouped_with_fiber=False,
        is_from_pack=False,
        fiber_linked="",
        shared_bond_id="",
    ):
        self.order_id = order_id
        self.phone_number = phone_number
        self.iban = iban
        self.email = email
        self.sc_icc = sc_icc
        self.icc = icc
        self.has_sim = has_sim
        self.type = type
        self.previous_provider = previous_provider
        self.previous_owner_vat = previous_owner_vat
        self.previous_owner_name = previous_owner_name
        self.previous_owner_surname = previous_owner_surname
        self.product = product
        self.delivery_street = delivery_street
        self.delivery_city = delivery_city
        self.delivery_zip_code = delivery_zip_code
        self.delivery_state = delivery_state
        self.technology = technology
        self.sim_delivery_tracking_code = sim_delivery_tracking_code
        self.sales_team = sales_team
        self.activation_notes = activation_notes
        self.notes = notes
        self.is_grouped_with_fiber = is_grouped_with_fiber
        self.is_from_pack = is_from_pack
        self.fiber_linked = fiber_linked
        self.shared_bond_id = shared_bond_id
        self.contact_phone = contact_phone
