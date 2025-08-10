import math

COPPER_RESISTIVITY = 0.018  # ohm mm²/m
POWER_FACTOR = 0.9


def calc_current(power_kw, voltage_v):
    """Approximate motor current for the given power and voltage."""
    return power_kw * 1000 / (math.sqrt(3) * voltage_v * POWER_FACTOR)


def dimension_line(current_a, length_m, voltage_v, max_drop_percent):
    """Return (cross_section, drop_percent) for a given current."""
    for cs in [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50]:
        resistance = 2 * length_m * COPPER_RESISTIVITY / cs
        delta_u = math.sqrt(3) * current_a * resistance
        drop_pct = delta_u / voltage_v * 100
        if drop_pct <= max_drop_percent:
            return cs, drop_pct
    return cs, drop_pct

