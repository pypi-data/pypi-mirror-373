import json
from itertools import chain
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from funcy import compact

if TYPE_CHECKING:
    from rhino_health.lib.rhino_session import RhinoSession

from rhino_health.lib.metrics.base_metric import AggregatableMetric, MetricResponse


def get_cloud_aggregated_metric_data(
    session: "RhinoSession",
    dataset_uids: List[str],
    metric_configuration: AggregatableMetric,
) -> MetricResponse:
    metric_configuration_dict = metric_configuration.data()
    timeout_seconds = metric_configuration_dict.pop("timeout_seconds", None)
    custom_aggregation_method = metric_configuration.custom_aggregation_method
    metric_response = session.post(
        f"/projects/calculate_aggregate_metric/",
        data={
            "dataset_uids": dataset_uids,
            "metric_configuration": metric_configuration_dict,
            "timeout_seconds": timeout_seconds,
        },
    )
    parsed_response = metric_response.parsed_response
    response_output = parsed_response.get("output", None)

    if custom_aggregation_method:
        response_output = custom_metric_aggregator(
            metric_configuration.metric_name(),
            response_output,
            custom_aggregation_method,
            metric_configuration.group_by,
            metric_configuration.count_variable_name,
        )

    return metric_configuration.metric_response(
        output=response_output,
        metric_configuration_dict=metric_configuration_dict,
        dataset_uids=dataset_uids,
        session=session,
    )


def custom_metric_aggregator(
    metric_name: str,
    metric_results: List[Dict[str, Any]],
    aggregation_method: Callable,
    group_by: Optional[str] = None,
    count_variable: str = "variable",
) -> Dict[str, Any]:
    """
    Aggregates the results from the individual datasets into one.
    """
    if group_by is None:
        return aggregation_method(metric_name, metric_results, count_variable=count_variable)
    else:
        groups = set(chain.from_iterable(metric_result.keys() for metric_result in metric_results))
        grouped_results = {}
        for group in groups:
            group_result = compact(
                [metric_result.get(group, None) for metric_result in metric_results]
            )
            grouped_results[group] = aggregation_method(
                metric_name, group_result, count_variable=count_variable
            )
        return grouped_results
