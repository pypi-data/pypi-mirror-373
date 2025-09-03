def is_empty(str_val: str) -> bool:
    return not str_val or not (str_val and str_val.strip())

def safe_str_to_number(value):
    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    raise ValueError(f"'{value}' is not a valid number.")