from otrs_somconnexio.otrs_models.internet_data import InternetData


class FiberData(InternetData):
    service_type = "fiber"

    def __init__(self, **args):
        fiber_args = [
            "previous_contract_pon",
            "previous_contract_fiber_speed",
            "all_grouped_SIMS_recieved",
            "has_grouped_mobile_with_previous_owner",
            "product_ba_mm",
            "keep_landline",
        ]
        for key in fiber_args:
            setattr(self, key, args.get(key, ""))
            args.pop(key, None)

        super().__init__(**args)
