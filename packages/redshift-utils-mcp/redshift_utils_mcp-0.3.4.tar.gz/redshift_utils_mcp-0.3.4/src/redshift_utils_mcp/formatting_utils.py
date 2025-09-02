"""
Utilities for formatting query results.
"""

import logging
import json
import csv
import io
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _format_as_table(result: List[Dict[str, Any]]) -> str:
    """Formats the query result as a fixed-width text table."""
    if not result:
        return "Empty result set"

    if not all(isinstance(row, dict) for row in result):
        logger.warning("Cannot format as table: result contains non-dictionary items.")
        return "Error: Result contains non-dictionary items."

    if not result[0]:
        headers = []
    else:
        headers = list(result[0].keys())

    if not headers:
        for row in result[1:]:
            if row and isinstance(row, dict) and row.keys():
                headers = list(row.keys())
                break
        if not headers:
            if len(result) > 0:
                return (
                    f"Result set has {len(result)} row(s) but no column headers found."
                )
            else:
                return "Empty result set"

    col_widths = {header: len(header) for header in headers}
    for row in result:

        if not isinstance(row, dict):
            continue
        for header in headers:

            val_str = str(row.get(header, ""))
            col_widths[header] = max(col_widths[header], len(val_str))

    header_row = " | ".join(header.ljust(col_widths[header]) for header in headers)
    separator = "-+-".join("-" * col_widths[header] for header in headers)

    formatted_rows = []
    for row in result:

        if not isinstance(row, dict):
            formatted_rows.append("[Skipped non-dictionary row]")
            continue
        formatted_row = " | ".join(
            str(row.get(header, "")).ljust(col_widths[header]) for header in headers
        )
        formatted_rows.append(formatted_row)

    return f"{header_row}\n{separator}\n" + "\n".join(formatted_rows)


def format_result(result: List[Dict[str, Any]], format_type: str = "json") -> str:
    """Formats the query result in the specified format."""
    if not result:
        logger.debug("format_result called with empty result list.")
        return "No results found."

    format_type = format_type.lower()
    logger.debug(f"Formatting {len(result)} results as {format_type}")

    if format_type == "json":
        try:

            return json.dumps(result, indent=2, default=str)
        except TypeError as e:
            logger.error(f"Error formatting result as JSON: {e}", exc_info=True)
            return f"Error formatting as JSON: {e}"

    elif format_type == "csv":
        try:
            output = io.StringIO()
            if result and isinstance(result[0], dict) and result[0].keys():
                fieldnames = list(result[0].keys())
                writer = csv.DictWriter(
                    output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL
                )
                writer.writeheader()
                dict_rows = [row for row in result if isinstance(row, dict)]
                writer.writerows(dict_rows)
            elif result:
                logger.warning(
                    "Could not determine CSV headers from the first result item."
                )
                output.write("Error: Could not determine CSV headers.")

            return output.getvalue()
        except (IOError, csv.Error, AttributeError) as e:
            logger.error(f"Error formatting result as CSV: {e}", exc_info=True)
            return f"Error generating CSV: {e}"

    elif format_type == "table":
        try:
            return _format_as_table(result)
        except Exception as e:
            logger.error(f"Error formatting result as table: {e}", exc_info=True)
            return f"Error generating table: {e}"

    else:
        logger.warning(f"Unsupported format requested: {format_type}")
        return f"Unsupported format: {format_type}. Use 'json', 'table', or 'csv'."
