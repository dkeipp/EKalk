import math

COPPER_RESISTIVITY = 0.018  # ohm mm²/m
POWER_FACTOR = 0.9


def dimension_line(power_kw, length_m, voltage_v, max_drop_percent):
    """Return (current, cross_section, drop_percent)."""
    current = power_kw * 1000 / (math.sqrt(3) * voltage_v * POWER_FACTOR)
    for cs in [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50]:
        resistance = 2 * length_m * COPPER_RESISTIVITY / cs
        delta_u = math.sqrt(3) * current * resistance
        drop_pct = delta_u / voltage_v * 100
        if drop_pct <= max_drop_percent:
            return current, cs, drop_pct
    return current, cs, drop_pct
