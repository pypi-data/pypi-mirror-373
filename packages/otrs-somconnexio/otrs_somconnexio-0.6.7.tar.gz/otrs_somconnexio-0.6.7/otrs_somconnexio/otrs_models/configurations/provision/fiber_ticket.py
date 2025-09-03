# coding: utf-8
class FiberTicketConfiguration:
    process_id = "Process-2a8a97fe837ce3c1906f524decb6fa6d"
    activity_id = "Activity-862a6517cdbf72be58b0b1b3a9e42f98"
    type = "Petición"
    SLA = "No pendent resposta"
    service = "Banda Ancha::Fibra::Provisió Fibra"
    queue_id = 31
    state = "new"
    priority = "3 normal"

    def __init__(self, otrs_configuration=None):
        # Deprecated - Only used with Tryton
        if otrs_configuration:
            self.process_id = otrs_configuration.fiber_process_id
            self.activity_id = otrs_configuration.fiber_activity_id
            self.type = otrs_configuration.fiber_ticket_type
            self.queue_id = otrs_configuration.fiber_ticket_queue_id
            self.state = otrs_configuration.fiber_ticket_state
            # We need to mantain this typo because is in a Tryton model field.
            self.priority = otrs_configuration.fiber_ticket_proprity
