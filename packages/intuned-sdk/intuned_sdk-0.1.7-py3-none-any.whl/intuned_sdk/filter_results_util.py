from typing import Any
from typing import Dict
from typing import List

from .process_dates import is_date_in_last_x_days
from .process_dates import process_date


def filter_results(
    results: List[Dict[str, Any]], params: Dict[str, Any]
) -> List[Dict[str, Any]]:
    filter_last_x_days = params.get("filter_last_x_days", None)
    latest_x_items = params.get("latest_x_items", None)
    if latest_x_items is None and filter_last_x_days is None:
        return results
    filtered_results: List[Dict[str, Any]] = []
    if filter_last_x_days:
        for result in results:
            if result.get("issue_date"):
                issue_date_datetime = process_date(result["issue_date"])
                if issue_date_datetime is None or is_date_in_last_x_days(
                    issue_date_datetime, filter_last_x_days
                ):
                    filtered_results.append(result)
            else:
                filtered_results.append(result)
    if latest_x_items is not None and filter_last_x_days is None:
        filtered_results = results[:latest_x_items]
    elif latest_x_items is not None and filter_last_x_days is not None:
        filtered_results = filtered_results[:latest_x_items]
    return filtered_results
