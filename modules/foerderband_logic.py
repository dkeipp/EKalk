def foerderband_schritt1(params):
    power = params.get("MotorLeistung", 0)
    params["Nennstrom"] = power * 2  # Platzhalter-Berechnung
    return params
