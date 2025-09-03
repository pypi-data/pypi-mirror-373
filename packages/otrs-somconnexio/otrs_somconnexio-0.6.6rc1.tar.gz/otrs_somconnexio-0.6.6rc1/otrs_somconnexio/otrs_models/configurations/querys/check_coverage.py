class CheckCoverageConfiguration:
    process_id = "Process-be8cf222949132c9fae1bb74615a5ae4"
    activity_id = "Activity-df0c0c05df090639bb592a6d2af2d893"
    type = "Petición"
    state = "new"
    priority = "3 normal"


class CheckCoverageCATConfiguration(CheckCoverageConfiguration):
    subject = "Consulta de cobertura (cat)"
    queue_id = 42


class CheckCoverageESConfiguration(CheckCoverageConfiguration):
    subject = "Consulta de cobertura (es)"
    queue_id = 43
