def calculate(params):
    currents = params.get("motor_currents", [])
    total_current = sum(currents)
    required = total_current * 0.75
    sizes = [63, 125, 250, 400, 630]
    suggested = next((s for s in sizes if s >= required), sizes[-1])
    params["main_switch_size"] = f"{suggested}A"
    params["needs_supply_field"] = suggested >= 400
    if suggested:
        reserve = (suggested - required) / suggested * 100
    else:
        reserve = 0
    params["capacity_reserve_percent"] = round(reserve, 2)
    return params
