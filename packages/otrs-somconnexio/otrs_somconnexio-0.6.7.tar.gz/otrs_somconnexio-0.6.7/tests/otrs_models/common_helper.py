def dynamic_fields_to_dct(dynamic_fields):
    """
    Convert an object in a dict with the name of the dynamic
    field as key and the value as value.
    """
    dct = {}
    for df in dynamic_fields:
        dct[df.name] = df.value
    return dct
