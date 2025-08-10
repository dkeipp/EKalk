import math
from .calc_utils import dimension_line, POWER_FACTOR


def calculate(params):
    voltage = int(str(params.get("Netzspannung", "0V")).rstrip("V"))
    freq = params.get("Frequenz")
    motor_voltage = voltage / math.sqrt(3) if params.get("StartArt") == "FU" and freq == 87 else voltage
    length = params.get("Laenge", 0) + params.get("AvgCableLength", 0)
    drives = params.get("Antriebe", 1)
    common = params.get("GemeinsamerStarter", False)

    def build_components(power_kw, current):
        if params.get("StartArt") == "DOL":
            return [
                {"Typ": "Motorschutz", "Leistungsklasse": f"{power_kw} kW", "Nennstrom": round(current, 2), "Class": "10A"},
                {"Typ": "Schütz", "Leistungsklasse": f"{power_kw} kW", "Nennstrom": round(current, 2)},
            ]
        else:
            return [
                {"Typ": "Leitungsschutz", "Leistungsklasse": f"{power_kw} kW", "Nennstrom": round(current, 2)},
                {"Typ": "Frequenzumrichter", "Leistungsklasse": f"{power_kw} kW", "Nennstrom": round(current, 2)},
            ]

    if common or drives == 1:
        power = params.get("MotorLeistung", 0) * drives if common else params.get("MotorLeistung", 0)
        motor_current = power * 1000 / (math.sqrt(3) * motor_voltage * POWER_FACTOR)
        current, cross_section, drop_pct = dimension_line(
            power, length, motor_voltage, params.get("MaxSpannungsabfall", 0)
        )
        params.update(
            {
                "LeistungskabelLaenge": length,
                "MotorSpannung": round(motor_voltage, 2),
                "Motorstrom": round(motor_current, 2),
                "Nennstrom": round(current, 2),
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
        motor_current = power * 1000 / (math.sqrt(3) * motor_voltage * POWER_FACTOR)
        for _ in range(drives):
            current, cross_section, drop_pct = dimension_line(
                power, length, motor_voltage, params.get("MaxSpannungsabfall", 0)
            )
            drive_results.append(
                {
                    "LeistungskabelLaenge": length,
                    "MotorSpannung": round(motor_voltage, 2),
                    "Motorstrom": round(motor_current, 2),
                    "Nennstrom": round(current, 2),
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

