class AddDataTicketConfiguration:
    process_id = "Process-7f03577ba04a39dbc9e0fe0d2c6144df"
    activity_id = "Activity-d621f2e21d7583c0dffc7569cd3c9f59"
    queue_id = 105
    subject = "Sol·licitud abonament addicional oficina virtual"
    type = "Petición"
    state = "new"
    priority = "3 normal"


class AddDataTicketRequestedConfiguration(AddDataTicketConfiguration):
    queue_id = 104
    state = "open"
