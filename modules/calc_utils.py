import math

COPPER_RESISTIVITY = 0.018  # ohm mm²/m



def calc_current(power_kw, voltage_v, safety_factor=1.01):
    """
    Berechnet den geschätzten Nennstrom eines Drehstrommotors
    für gegebene mechanische Nennleistung (kW) und Netz-Nennspannung (V).

    Annahmen / Hintergrund:
    - 4-poliger Käfigläufermotor, 50 Hz, IE2/IE3 Effizienzklasse
    - Leistungsfaktor (cos φ) und Wirkungsgrad (η) werden zu einem
      kombinierten Faktor η*cosφ zusammengefasst
    - Dieser Faktor ist leistungsskalierend, d.h. kleine Motoren haben
      einen schlechteren Wert, große Motoren einen besseren
    - Die Schätzung basiert auf einer logarithmischen Regression aus
      typischen Herstellerangaben (0,75–45 kW)
    - Der Faktor wird auf einen konservativen Bereich (0.62…0.87)
      begrenzt, um unrealistische Werte zu vermeiden
    - safety_factor > 1.0 gibt einen Aufschlag auf den Strom (z.B. 1.05
      = 5 % Reserve)

    Formel:
        I = (P_el) / (sqrt(3) * U * η * cosφ)
        P_el = P_mech / η  --> η steckt hier schon im gemeinsamen Faktor drin
        η*cosφ ≈ 0.6557 + 0.05604 * ln(P[kW])   (Regression)

    Parameter:
        power_kw      (float)  : mechanische Nennleistung in kW
        voltage_v     (float)  : Leiterspannung (LL) in Volt
        safety_factor (float)  : optionaler Zuschlagfaktor (default 1.05)

    Rückgabe:
        Strom in Ampere (float)
    """
    if not 0.75 <= power_kw <= 45:
        raise ValueError("power_kw outside supported range (0.75-45 kW)")
    # Kombinierter Faktor η*cosφ anhand einer logarithmischen Näherung
    eff_cosphi = 0.6557219 + 0.0560407 * math.log(power_kw)
    # Faktor auf realistische Grenzen begrenzen
    eff_cosphi = max(0.62, min(0.87, eff_cosphi))
    # Stromberechnung (Leistung in Watt)
    return safety_factor * power_kw * 1000 / (math.sqrt(3) * voltage_v * eff_cosphi)


def dimension_line(current_a, length_m, voltage_v, max_drop_percent):
    """Return (cross_section, drop_percent) for a given current.

    Raises ValueError if no suitable cross section is found within the
    predefined range.
    """
    for cs in [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50]:
        resistance = 2 * length_m * COPPER_RESISTIVITY / cs
        delta_u = math.sqrt(3) * current_a * resistance
        drop_pct = delta_u / voltage_v * 100
        if drop_pct <= max_drop_percent:
            return cs, drop_pct
    raise ValueError("requirements exceed available cable sizes")


def calc_voltage_drop(current_a, length_m, voltage_v, cross_section):
    """Return voltage drop percentage for a given cross section.

    Raises ValueError if the cross section is not one of the supported
    standard sizes.
    """
    valid = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50]
    if cross_section not in valid:
        raise ValueError("cross_section outside supported sizes")
    resistance = 2 * length_m * COPPER_RESISTIVITY / cross_section
    delta_u = math.sqrt(3) * current_a * resistance
    return delta_u / voltage_v * 100

