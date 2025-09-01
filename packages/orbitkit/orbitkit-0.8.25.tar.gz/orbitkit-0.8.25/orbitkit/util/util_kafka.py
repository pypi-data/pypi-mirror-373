from datetime import datetime


def wrapper_k_ignore(item: dict) -> dict:
    item["x_others"]["k_ignore"] = int(datetime.now().timestamp() * 1000)
    return item
