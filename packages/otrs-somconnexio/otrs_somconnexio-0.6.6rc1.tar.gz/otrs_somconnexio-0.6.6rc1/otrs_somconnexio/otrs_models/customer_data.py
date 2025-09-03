class CustomerData:
    def __init__(
        self,
        id,
        vat_number,
        name,
        first_name,
        street,
        city,
        zip,
        subdivision,
        has_active_contracts,
        language,
    ):
        self.id = id
        self.vat_number = vat_number
        self.name = name
        self.first_name = first_name
        self.street = street
        self.city = city
        self.zip = zip
        self.subdivision = subdivision
        self.has_active_contracts = has_active_contracts
        self.language = language
