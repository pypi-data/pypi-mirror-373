class ServiceMappingServices:
    SERVICES = {
        "Mobil": "mobile",
        "Fibra": "fiber",
        "ADSL": "adsl",
        "ADSL+100min": "adsl100",
        "ADSL+1000min": "adsl1000",
        "4G": "4g",
        "Mixta": "mixta",
    }

    @classmethod
    def service(cls, otrs_service):
        return cls.SERVICES[otrs_service]
