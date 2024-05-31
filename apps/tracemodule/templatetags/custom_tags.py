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