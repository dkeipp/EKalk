from .calc_utils import dimension_line


def calculate(params):
    voltage = int(str(params.get("Netzspannung", "0V")).rstrip("V"))
    length = params.get("Laenge", 0) + params.get("AvgCableLength", 0)
    current, cross_section, drop_pct = dimension_line(
        params.get("MotorLeistung", 0),
        length,
        voltage,
        params.get("MaxSpannungsabfall", 0),
    )
    params.update(
        {
            "LeistungskabelLaenge": length,
            "Nennstrom": round(current, 2),
            "LeitungQuerschnitt": cross_section,
            "SpannungsabfallProzent": round(drop_pct, 2),
            "Schaltschrank": [
                "Motorschutz",
                "Schütz",
            ]
            if params.get("StartArt") == "DOL"
            else ["Leitungsschutz", "Frequenzumrichter"],
            "KabelrohrLaenge": params.get("Laenge", 0),
        }
    )
    return params
