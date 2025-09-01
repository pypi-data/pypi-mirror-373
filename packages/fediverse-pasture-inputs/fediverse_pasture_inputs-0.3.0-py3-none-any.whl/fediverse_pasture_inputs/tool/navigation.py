from collections import defaultdict

from fediverse_pasture_inputs import available

group_names = [
    "Recommended Objects",
    "HTML Tags",
    "Object Content",
    "Object Properties",
    "Technical Properties",
]


def order_available_by_group():
    result = defaultdict(list)

    for _, input_data in available.items():
        result[input_data.group].append(input_data)

    return result


def navigation_string(prefix: str = "") -> str:
    result = []

    ordered_by_group = order_available_by_group()

    for name in group_names:
        result.append(f"""- "{name}":\n""")

        entries = sorted(ordered_by_group[name], key=lambda x: x.title)

        for entry in entries:
            result.append(f"""  - "{entry.title}": "{prefix}{entry.filename}"\n""")

    return result
