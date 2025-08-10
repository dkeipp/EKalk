def calculate(params):
    size_str = str(params.get("main_switch_size", "0A"))
    try:
        size = int(size_str.rstrip("A"))
    except ValueError:
        size = 0
    params["needs_supply_field"] = size >= 400
    return params
