import math
from .calc_utils import calc_current, dimension_line


def calculate(params):
    voltage = int(str(params.get("Netzspannung", "0V")).rstrip("V"))
    freq = params.get("Frequenz")
    motor_voltage = voltage / math.sqrt(3) if params.get("StartArt") == "FU" and freq == 87 else voltage
    length = params.get("Laenge", 0) + params.get("AvgCableLength", 0)
    drives = params.get("Antriebe", 1)
    common = params.get("GemeinsamerStarter", True)

    def build_components(power_kw, current):
        return [
            {"Typ": "Leitungsschutz", "Nennstrom": round(current, 2)},
            {"Typ": "Frequenzumrichter", "Nennstrom": round(current, 2)},
        ]

    if common or drives == 1:
        power = params.get("MotorLeistung", 0) * drives if common else params.get("MotorLeistung", 0)
        motor_current = calc_current(power, motor_voltage)
        cross_section, drop_pct = dimension_line(
            motor_current, length, motor_voltage, params.get("MaxSpannungsabfall", 0)
        )
        params.update(
            {
                "LeistungskabelLaenge": length,
                "MotorSpannung": round(motor_voltage, 2),
                "Motornennstrom": round(motor_current, 2),
                "LeitungQuerschnitt": cross_section,
                "SpannungsabfallProzent": round(drop_pct, 2),
                "Schaltschrank": build_components(power, motor_current),
                "KabelrohrLaenge": params.get("Laenge", 0),
            }
        )
    else:
        drive_results = []
        components = []
        power = params.get("MotorLeistung", 0)
        motor_current = calc_current(power, motor_voltage)
        for _ in range(drives):
            cross_section, drop_pct = dimension_line(
                motor_current, length, motor_voltage, params.get("MaxSpannungsabfall", 0)
            )
            drive_results.append(
                {
                    "LeistungskabelLaenge": length,
                    "MotorSpannung": round(motor_voltage, 2),
                    "Motornennstrom": round(motor_current, 2),
                    "LeitungQuerschnitt": cross_section,
                    "SpannungsabfallProzent": round(drop_pct, 2),
                }
            )
            components.extend(build_components(power, motor_current))
        params.update(
            {
                "Triebe": drive_results,
                "Schaltschrank": components,
                "KabelrohrLaenge": params.get("Laenge", 0),
            }
        )
    return params

