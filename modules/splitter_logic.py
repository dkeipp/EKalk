import math
from .calc_utils import calc_current, dimension_line, calc_voltage_drop


def calculate(params):
    voltage = int(str(params.get("supply_voltage", "0V")).rstrip("V"))
    freq = params.get("frequency")
    motor_voltage = voltage / math.sqrt(3) if params.get("start_type") == "FU" and freq == 87 else voltage
    length = params.get("length", 0) + params.get("avg_cable_length", 0)
    drives = params.get("drive_count", 1)
    common = params.get("common_starter", True)

    def build_components(power_kw, current):
        return [
            {"type": "circuit_breaker", "rated_current": round(current, 2)},
            {"type": "frequency_inverter", "rated_current": round(current, 2)},
        ]

    provided_cs = params.get("cable_cross_section")

    if common or drives == 1:
        power = params.get("motor_rated_power", 0) * drives if common else params.get("motor_rated_power", 0)
        motor_current = calc_current(power, motor_voltage)
        if provided_cs is not None:
            drop_pct = calc_voltage_drop(motor_current, length, motor_voltage, provided_cs)
            cross_section = provided_cs
        else:
            cross_section, drop_pct = dimension_line(
                motor_current, length, motor_voltage, params.get("max_voltage_drop", 0)
            )
        params.update(
            {
                "power_cable_length": length,
                "motor_voltage": round(motor_voltage, 2),
                "motor_rated_current": round(motor_current, 2),
                "cable_cross_section": cross_section,
                "voltage_drop_percent": round(drop_pct, 2),
                "control_cabinet": build_components(power, motor_current),
                "conduit_length": params.get("length", 0),
            }
        )
    else:
        drive_results = []
        components = []
        power = params.get("motor_rated_power", 0)
        motor_current = calc_current(power, motor_voltage)
        for _ in range(drives):
            if provided_cs is not None:
                drop_pct = calc_voltage_drop(motor_current, length, motor_voltage, provided_cs)
                cross_section = provided_cs
            else:
                cross_section, drop_pct = dimension_line(
                    motor_current, length, motor_voltage, params.get("max_voltage_drop", 0)
                )
            drive_results.append(
                {
                    "power_cable_length": length,
                    "motor_voltage": round(motor_voltage, 2),
                    "motor_rated_current": round(motor_current, 2),
                    "cable_cross_section": cross_section,
                    "voltage_drop_percent": round(drop_pct, 2),
                }
            )
            components.extend(build_components(power, motor_current))
        params.update(
            {
                "drives": drive_results,
                "control_cabinet": components,
                "conduit_length": params.get("length", 0),
            }
        )
    return params

