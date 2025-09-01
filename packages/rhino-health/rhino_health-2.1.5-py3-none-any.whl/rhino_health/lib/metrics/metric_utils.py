import ast
from typing import Any, Dict, Tuple, Union


def nested_metric_groups(grouped_metric_results: Dict[Union[Tuple, str], Any]) -> Dict[str, Any]:
    """
    Converts a dictionary of grouped metrics to a nested dictionary

    Examples
    --------
    >>> input = {"('F', False)": {'count': 20}, "('F', True)": {'count': 14}, "('M', False)": {'count': 17}, "('M', True)": {'count': 25}}
    >>> nested_metric_groups(input)
    {'F': {False: { 'count': 20 }, True: { 'count': 14} }, 'M': {False: { 'count': 17 }, True: { 'count': 25 }}}

    .. warning:: How groups are represented will likely change in the future and this function will change in future versions
    """
    new_output = {}
    for group_tuple, group_values in grouped_metric_results.items():
        current_location = new_output
        if isinstance(group_tuple, str):
            # If multiple groups we get a str tuple which needs ast literal eval
            try:
                group_tuple = ast.literal_eval(group_tuple)
            except (ValueError, TypeError, SyntaxError):
                # If it's not multiple groups the ast will fail, treat as a single group
                group_tuple = (group_tuple,)
        nested_dict = new_output
        for key in group_tuple[:-1]:
            nested_dict = nested_dict.setdefault(key, {})
        nested_dict[group_tuple[-1]] = group_values
    return new_output
