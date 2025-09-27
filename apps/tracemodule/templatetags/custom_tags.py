from django import template

register = template.Library()

@register.filter
def unique_growers(growers):
    seen = set()
    unique_list = []
    # print("growers", growers)
    for grower in growers:
        if grower["grower_name"] not in seen:
            unique_list.append(grower)
            seen.add(grower["grower_name"])
    return unique_list

@register.filter
def unique_by_field_name(value):
    """Returns a list of objects with unique field_name"""
    seen = set()
    unique_items = []
    for item in value:
        if item["field_name"] not in seen:
            unique_items.append(item)
            seen.add(item["field_name"])
    return unique_items

@register.filter
def unique_by_shipment_id(value):
    """Returns a list of objects with unique shipment id"""
    seen = set()
    unique_items = []
    for item in value:
        if item["shipment_id"] not in seen:
            unique_items.append(item)
            seen.add(item["shipment_id"])
    return unique_items

@register.filter
def unique_processor(processors):
    seen = set()
    unique_list = []
    # print("growers", processors)
    for processor in processors:
        if processor["processor_name"] not in seen:
            unique_list.append(processor)
            seen.add(processor["processor_name"])
    return unique_list

@register.filter
def unique1_processor(processors):
    seen = set()
    unique_list = []
    # print("growers", processors)
    for processor in processors:
        if processor["processor2_name"] not in seen:
            unique_list.append(processor)
            seen.add(processor["processor2_name"])
    return unique_list


@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return '' 
    
    
@register.filter
def unique_customer(customers):
    seen = set()
    unique_list = []
    # print("growers", processors)
    for customer in customers:
        if customer["customer_name"] not in seen:
            unique_list.append(customer)
            seen.add(customer["customer_name"])
    return unique_list

@register.filter
def unique_warehouse(warehouses):
    seen = set()
    unique_list = []
    # print("growers", processors)
    for warehouse in warehouses:
        if warehouse["warehouse_name"] not in seen:
            unique_list.append(warehouse)
            seen.add(warehouse["warehouse_name"])
    return unique_list

@register.filter
def ordinal_day(value):
    """
    Adds ordinal suffix to the day of the month.
    Example: 1 -> 1st, 2 -> 2nd, 3 -> 3rd, etc.
    """
    try:
        value = int(value)
        if 10 <= value % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
        return f"{value}{suffix}"
    except (ValueError, TypeError):
        return value
    

@register.filter
def unique_by_diversion(shipments):
    result = []

    for shipment in shipments:
        base = shipment.copy()
        crops = shipment.get("crops", [])
        carrier_id = shipment.get("carrier_id")

        for crop in crops:
            # If diversion exists, split it per diversion
            if crop.get("prev_waybill_number") or crop.get("diversion_date"):
                entry = {
                    **base,
                    "carrier_id": carrier_id,
                    "crops": [crop],
                }
                result.append(entry)
            else:
                entry = {
                    **base,
                    "carrier_id": carrier_id,
                    "crops": [crop],
                }
                result.append(entry)

    return result
