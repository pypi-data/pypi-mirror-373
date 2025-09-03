class ChangeOwnerConfiguration:
    process_id = "Process-975190079a628ddf1eb4f0188dce2e4a"
    type = "Petición"
    state = "new"
    priority = "3 normal"
    subject = "Sol·licitud canvi de titular oficina virtual"
    body = "Adjunta documentació titular actual"
    update_subject = "Resposta sol·licitud de canvi de titular oficina virtual"
    update_body = "Adjunta documentació nou titular"


class ChangeOwnerTicketConfiguration(ChangeOwnerConfiguration):
    queue_id = 236
    activity_id = "Activity-12c832820da79b425874b2bdf05fa512"


class ChangeOwnerPackTicketConfiguration(ChangeOwnerConfiguration):
    queue_id = 237
    activity_id = "Activity-0dc37160064a0aeccae2a0393cda1189"
