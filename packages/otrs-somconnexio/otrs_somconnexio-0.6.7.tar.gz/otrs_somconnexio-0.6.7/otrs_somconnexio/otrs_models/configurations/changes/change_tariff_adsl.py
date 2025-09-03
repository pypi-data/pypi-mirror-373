class ChangeTariffAdslConfiguration:
    type = "Petición"
    state = "new"
    priority = "3 normal"


class ChangeTariffTicketAdslOutLandlineConfig(ChangeTariffAdslConfiguration):
    process_id = "Process-75757fe8d1526118bf0a723fde97b217"
    activity_id = "Activity-4c41ac0caaa3601dff977822b7b83299"
    queue_id = 165
    subject = "OV Sol·licitud CT A SF/F SF"
    code_fiber = "SE_SC_REC_BA_F_300_SF"


class ChangeTariffTicketAdslLandlineConfig(ChangeTariffAdslConfiguration):
    process_id = "Process-5684ebe48aa930b2890e3ae0febc483d"
    activity_id = "Activity-6d1a466b85f7278eda75c4fec4e6ecfe"
    queue_id = 192
    subject = "OV Sol·licitud CT A F/F F"
    code_fiber = "SE_SC_REC_BA_F_300"
