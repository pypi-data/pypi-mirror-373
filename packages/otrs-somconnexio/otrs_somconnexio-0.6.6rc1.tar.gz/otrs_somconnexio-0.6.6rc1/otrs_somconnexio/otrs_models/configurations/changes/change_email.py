class ChangeEmailTicketConfiguration:
    process_id = "Process-b4243866849bc5c0c292f18100fad9d3"
    activity_id = "Activity-8cc76400ded45e7b408f6d3e0267a2c6"
    type = "Petición"
    state = "new"
    priority = "3 normal"


class ChangeEmailContractsConfiguration(ChangeEmailTicketConfiguration):
    queue_id = 174
    subject = "Sol·licitud canvi de email oficina virtual"


class ChangeEmailPersonalConfiguration(ChangeEmailTicketConfiguration):
    queue_id = 178
    subject = "Canvi d'email dades personals OV"
