from collections import namedtuple

FN_PLACEHOLDERS = namedtuple(
    "FN_PLACEHOLDERS",
    [
        "base_dir",
        "prodDate",
        "refDate",
        "DR",
        "DRyyyy",
        "DRmm",
        "DRdd",
        "DPyyyy",
        "DPmm",
        "DPdd",
    ],
)


def build_fn_placeholders(base_dir: str, ref_date: str, prod_date: str):
    ref_yyyy, ref_mm, ref_dd = ref_date[0:4], ref_date[4:6], ref_date[6:8]
    prod_yyyy, prod_mm, prod_dd = prod_date[0:4], prod_date[4:6], prod_date[6:8]

    return FN_PLACEHOLDERS(
        base_dir=base_dir,
        prodDate=prod_date,
        refDate=ref_date,
        DR=ref_date,
        DRyyyy=ref_yyyy,
        DRmm=ref_mm,
        DRdd=ref_dd,
        DPyyyy=prod_yyyy,
        DPmm=prod_mm,
        DPdd=prod_dd,
    )


def replace_placeholders(
    str_template: str, placeholders: FN_PLACEHOLDERS, other_placeholders: dict = None
):
    """
    Replace placeholders in a string template with values from named tuple placeholders and
    optionally from a dictionary of other placeholders. The other placeholders has higher priority.

    Args:
    - str_template (str): The string template where placeholders will be replaced.
    - placeholders (namedtuple): Named tuple containing values for placeholders.
    - other_placeholders (dict, optional): Dictionary containing additional placeholders and their values.
        It overwrites value in placeholders dict if a common value is present

    Returns:
    - str: The modified string with placeholders replaced.
    """
    dict_placeholders = placeholders._asdict()
    # If other_placeholders is provided, update dict_placeholders with its values - overwrite common parameters
    if other_placeholders is not None:
        dict_placeholders.update(other_placeholders)

    new_str = str_template
    # Replace each placeholder in the template with its corresponding value
    for placeholder, value in dict_placeholders.items():
        new_str = new_str.replace(f"{{{placeholder}}}", value)

    return new_str
