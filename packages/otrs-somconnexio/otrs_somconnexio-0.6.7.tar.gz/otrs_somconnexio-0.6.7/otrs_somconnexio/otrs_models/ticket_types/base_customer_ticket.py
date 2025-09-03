from .base_ticket import BaseTicket


class BaseCustomerTicket(BaseTicket):
    def _get_process_management_dynamic_fields(self):
        result = {
            "ProcessManagementProcessID": self._get_process_id(),
            "ProcessManagementActivityID": self._get_activity_id(),
        }

        for k, v in dict(result).items():
            if v is None:
                del result[k]

        return result

    def _get_type(self):
        return "Petición"

    def _get_activity_id(self):
        return self.configuration.activity_id

    def _get_process_id(self):
        return self.configuration.process_id
