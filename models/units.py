UNITS = ["kg", "g", "bolsa", "l", "ml", "unidad", "lata", "botella", "caja"]

def get_all():
    """
    Returns a list of all units.
    """
    return UNITS

def add_unit(unit):
    """
    Adds a new unit to the list if it does not already exist.
    :param unit: The unit to add.
    :return: True if the unit was added, False if it already exists.
    """
    if unit not in UNITS:
        UNITS.append(unit)
        return True
    return False