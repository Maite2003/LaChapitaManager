UNITS = ["kg", "g", "bolsa", "l", "ml", "unidad", "lata", "botella", "caja"]

def get_all():
    """
    Devuelve una lista de todas las unidades disponibles.
    """
    return UNITS

def add_unit(unit):
    """
    Agrega una nueva unidad a la lista si no existe.
    :param unit: Unidad a agregar.
    :return: True si se agregó, False si ya existía.
    """
    if unit not in UNITS:
        UNITS.append(unit)
        return True
    return False