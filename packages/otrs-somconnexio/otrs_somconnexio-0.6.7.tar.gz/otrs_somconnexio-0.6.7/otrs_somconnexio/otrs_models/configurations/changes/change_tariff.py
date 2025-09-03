# coding: utf-8
class ChangeTariffTicketConfiguration:
    process_id = "Process-f91240baa6e0146aecc70a9c97d6f84f"
    activity_id = "Activity-7117b19116339f88dc43767cd477f2be"
    type = "Petición"
    queue_id = 97
    state = "new"
    priority = "3 normal"

    def __init__(self, otrs_configuration=None):
        if otrs_configuration:
            self.process_id = otrs_configuration.mobile_process_id
            self.activity_id = otrs_configuration.mobile_activity_id
            self.type = otrs_configuration.mobile_ticket_type
            self.queue_id = otrs_configuration.mobile_ticket_queue_id
            self.state = otrs_configuration.mobile_ticket_state
            # We need to mantain this typo because is in a Tryton model field.
            self.priority = otrs_configuration.mobile_ticket_priority


class ChangeTariffExceptionalTicketConfiguration(ChangeTariffTicketConfiguration):
    process_id = "Process-68cb2bbbfeaf511c76285ff1ee35166b"
    activity_id = "Activity-24e02ae12857239254b4c1d1e76acbba"
    queue_id = 187


class ChangeTariffSharedBondTicketConfiguration(ChangeTariffTicketConfiguration):
    queue_id = 201
    activity_id = "Activity-0fa4168fb49ea8be15e7270d6ba2d1c3"
