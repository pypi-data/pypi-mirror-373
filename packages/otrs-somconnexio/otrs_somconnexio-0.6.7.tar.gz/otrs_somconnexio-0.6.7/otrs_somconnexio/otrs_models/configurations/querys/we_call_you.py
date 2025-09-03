class WeCallYouConfiguration:
    process_id = "Process-ecf037c9e125f692e0ccb1d82eba5d3a"
    activity_id = "Activity-1b94759f56e5b7ecf67e1330d1c6afab"
    type = "Petición"
    state = "new"
    priority = "3 normal"


class WeCallYouCATConfiguration(WeCallYouConfiguration):
    queue_id = 144
    subject = "Formulari 'Vols que et truquem?' (CAT)"


class WeCallYouESConfiguration(WeCallYouConfiguration):
    queue_id = 145
    subject = "Formulari 'Vols que et truquem?' (ES)"


class WeCallYouCompanyCATConfiguration(WeCallYouConfiguration):
    queue_id = 230
    subject = "Formulari 'Vols que et truquem?' - Empreses (CAT)"


class WeCallYouCompanyESConfiguration(WeCallYouConfiguration):
    queue_id = 231
    subject = "Formulari 'Vols que et truquem?' - Empreses (ES)"
