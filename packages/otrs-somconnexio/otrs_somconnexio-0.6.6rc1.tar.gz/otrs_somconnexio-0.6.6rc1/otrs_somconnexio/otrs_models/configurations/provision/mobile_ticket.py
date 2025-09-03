# coding: utf-8
class MobileTicketConfiguration:
    process_id = "Process-325351399237c1e69144b17e471b1b51"
    activity_id = "Activity-90f09a366cd9426695ef0e21faeb4ed2"
    type = "Petición"
    queue_id = 71
    state = "new"
    SLA = "No pendent resposta"
    service = "Mòbil"
    priority = "3 normal"

    def __init__(self, otrs_configuration=None):
        if otrs_configuration:
            self.process_id = otrs_configuration.mobile_process_id
            self.activity_id = otrs_configuration.mobile_activity_id
            self.type = otrs_configuration.mobile_ticket_type
            self.queue_id = otrs_configuration.mobile_ticket_queue_id
            self.state = otrs_configuration.mobile_ticket_state
            self.priority = otrs_configuration.mobile_ticket_priority


class MobileTicketPausedConfiguration(MobileTicketConfiguration):
    activity_id = "Activity-ad31188b18cac0d1af222360fce65757"
    queue_id = 197


class MobileTicketCompletedConfiguration(MobileTicketConfiguration):
    activity_id = "Activity-32e86e86b387b7311a6258b783f16a29"
    queue_id = 198


class MobileTicketRequestedConfiguration(MobileTicketConfiguration):
    activity_id = "Activity-19187651eb9900b7c239d6b168c0b6f3"
    queue_id = 72


class MobileTicketPlatformIntroducedConfiguration(MobileTicketConfiguration):
    activity_id = "Activity-87200fa0f40f91ebd8a36ad2d1ed45c2"
    queue_id = 75


class MobileTicketActivationScheduledConfiguration(MobileTicketConfiguration):
    activity_id = "Activity-31525744004897d761133c9bee9ef6d9"
    queue_id = 73
