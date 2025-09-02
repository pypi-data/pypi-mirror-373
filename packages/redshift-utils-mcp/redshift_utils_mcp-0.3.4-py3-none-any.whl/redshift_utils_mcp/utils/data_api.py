import os
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple

import boto3


class DataApiConfigError(ValueError):
    """Error related to missing or invalid Redshift Data API configuration.

    Indicates that required environment variables for connecting to the
    Redshift Data API are missing or improperly formatted. Inherits from
    ValueError as it represents an issue with configuration values.
    """

    pass


class DataApiError(Exception):
    """Base exception for errors during Redshift Data API interactions.

    This serves as a general catch-all for issues encountered while
    communicating with the AWS Redshift Data API, excluding specific
    configuration or SQL execution failures which have their own exceptions.
    """

    pass


class SqlExecutionError(DataApiError):
    """Error specifically during the execution of a SQL statement via Data API.

    Raised when a submitted SQL statement results in a 'FAILED' or 'ABORTED'
    status according to the Redshift Data API. Contains additional details
    about the SQL error if available.

    Attributes:
        sql_state: The SQLSTATE code associated with the error, if provided by the API.
        error_code: A specific error code associated with the failure, if provided.
    """

    def __init__(
        self,
        message: str,
        sql_state: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        """Initializes the SqlExecutionError.

        Args:
            message: The main error message describing the failure.
            sql_state: Optional SQLSTATE code.
            error_code: Optional specific error code.
        """
        super().__init__(message)
        self.sql_state: Optional[str] = sql_state
        self.error_code: Optional[str] = error_code


class DataApiTimeoutError(DataApiError):
    """Error raised when polling for Redshift Data API results times out.

    Indicates that the maximum number of polling attempts was reached before
    the SQL statement reached a terminal state ('FINISHED', 'FAILED', 'ABORTED').
    """

    pass


@dataclass
class DataApiConfig:
    """Configuration parameters for connecting to Redshift Data API.

    Holds all necessary details required to establish a connection and
    execute statements against a specific Redshift cluster using the Data API.

    Attributes:
        cluster_id: The identifier of the target Redshift cluster.
        database: The name of the database to connect to within the cluster.
        secret_arn: The ARN of the AWS Secrets Manager secret containing credentials.
        region: The AWS region where the cluster and secret reside.
        aws_profile: Optional AWS named profile to use for credentials.
    """

    cluster_id: str
    database: str
    secret_arn: str
    region: str
    aws_profile: Optional[str] = None


def get_data_api_config() -> DataApiConfig:
    """Retrieves Redshift Data API configuration from environment variables.

    Reads the following environment variables:
    - REDSHIFT_CLUSTER_ID (required)
    - REDSHIFT_DATABASE (required)
    - REDSHIFT_SECRET_ARN (required)
    - AWS_REGION or AWS_DEFAULT_REGION (required, AWS_REGION preferred)
    - AWS_PROFILE (optional)

    Raises:
        DataApiConfigError: If any required environment variable is missing.

    Returns:
        DataApiConfig: An object containing the validated configuration.
    """
    cluster_id: Optional[str] = os.environ.get("REDSHIFT_CLUSTER_ID")
    database: Optional[str] = os.environ.get("REDSHIFT_DATABASE")
    secret_arn: Optional[str] = os.environ.get("REDSHIFT_SECRET_ARN")
    region: Optional[str] = os.environ.get("AWS_REGION") or os.environ.get(
        "AWS_DEFAULT_REGION"
    )
    aws_profile: Optional[str] = os.environ.get("AWS_PROFILE")

    missing_vars: List[str] = []
    if not cluster_id:
        missing_vars.append("REDSHIFT_CLUSTER_ID")
    if not database:
        missing_vars.append("REDSHIFT_DATABASE")
    if not secret_arn:
        missing_vars.append("REDSHIFT_SECRET_ARN")
    if not region:
        missing_vars.append("AWS_REGION or AWS_DEFAULT_REGION")

    if missing_vars:
        raise DataApiConfigError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    assert cluster_id is not None
    assert database is not None
    assert secret_arn is not None
    assert region is not None

    return DataApiConfig(
        cluster_id=cluster_id,
        database=database,
        secret_arn=secret_arn,
        region=region,
        aws_profile=aws_profile,
    )


POLL_INTERVAL_S: float = 1.0
MAX_POLLS: int = 300

logger: logging.Logger = logging.getLogger(__name__)


async def execute_sql(
    config: DataApiConfig,
    sql: str,
    params: Optional[List[Tuple[str, Any]]] = None,
    poll_interval_s: float = POLL_INTERVAL_S,
    max_polls: int = MAX_POLLS,
) -> Dict[str, Any]:
    """Executes a SQL statement using the Redshift Data API and retrieves results.

    Handles statement submission, status polling, result pagination, and basic
    result parsing into a list of dictionaries.

    Args:
        config: DataApiConfig object with connection details.
        sql: The SQL query string to execute.
        params: Optional list of tuples containing parameter name and value.
                Values will be converted to strings. Example: [('id', 1), ('name', 'test')]
        poll_interval_s: Time in seconds between polling attempts for statement status.
        max_polls: Maximum number of polling attempts before timing out.

    Raises:
        DataApiConfigError: If there's an issue with AWS credentials or configuration
                            detected during the boto3 client interaction (e.g., AccessDenied).
        DataApiError: For general or unexpected AWS Data API errors during the process.
        SqlExecutionError: If the SQL statement execution results in a 'FAILED' or
                           'ABORTED' status.
        DataApiTimeoutError: If polling for the statement's final status exceeds the
                             maximum attempts defined by `max_polls`.

    Returns:
        A dictionary containing:
        - 'rows': A list of dictionaries representing the result rows. Each dictionary
                  maps column names (str) to their corresponding values (Any).
                  Empty list if no results or on error.
        - 'error': An error message string if an exception occurred, otherwise None.
    """
    session_kwargs: Dict[str, str] = {"region_name": config.region}
    if config.aws_profile:
        session_kwargs["profile_name"] = config.aws_profile

    try:
        session: boto3.Session = await asyncio.to_thread(
            boto3.Session, **session_kwargs
        )
        client: Any = await asyncio.to_thread(session.client, "redshift-data")

        boto_params: List[Dict[str, Any]] = []
        if params:

            for name, value in params:
                sql_parameter: Dict[str, Any] = {"name": name}

                if value is None:
                    sql_parameter["isNull"] = True
                else:

                    sql_parameter["value"] = str(value)
                boto_params.append(sql_parameter)

        logger.debug(
            f"Executing SQL (Cluster: {config.cluster_id}, DB: {config.database}): {sql[:100]}..."
        )

        execute_kwargs: Dict[str, Any] = {
            "ClusterIdentifier": config.cluster_id,
            "Database": config.database,
            "SecretArn": config.secret_arn,
            "Sql": sql,
        }
        if boto_params:
            execute_kwargs["Parameters"] = boto_params

        logger.debug(f"Passing parameters to boto3: {boto_params}")
        exec_response: Dict[str, Any] = await asyncio.to_thread(
            client.execute_statement, **execute_kwargs
        )
        statement_id: str = exec_response["Id"]
        logger.info(f"Statement ID: {statement_id} submitted for SQL: {sql[:100]}...")

        poll_count: int = 0
        desc_response: Dict[str, Any] = {}
        while poll_count < max_polls:
            poll_count += 1
            logger.debug(
                f"Polling statement {statement_id}, attempt {poll_count}/{max_polls}"
            )
            desc_response = await asyncio.to_thread(
                client.describe_statement, Id=statement_id
            )
            status: str = desc_response["Status"]

            if status == "FINISHED":
                logger.info(f"Statement {statement_id} finished.")
                break
            elif status in ["FAILED", "ABORTED"]:
                error_msg: str = desc_response.get("Error", "Unknown error")
                redshift_error_code: Optional[str] = desc_response.get("QueryString")
                redshift_sql_state: Optional[str] = desc_response.get(
                    "RedshiftSqlState"
                )
                logger.error(f"Statement {statement_id} {status.lower()}: {error_msg}")
                raise SqlExecutionError(
                    f"SQL execution {status.lower()}: {error_msg}",
                    sql_state=redshift_sql_state,
                    error_code=redshift_error_code,
                )
            elif status in ["SUBMITTED", "PICKED", "STARTED"]:
                await asyncio.sleep(poll_interval_s)
            else:
                logger.warning(
                    f"Statement {statement_id} has unexpected status: {status}"
                )
                await asyncio.sleep(poll_interval_s)
        else:
            timeout_seconds: float = max_polls * poll_interval_s
            logger.error(
                f"Polling for statement {statement_id} timed out after {poll_count} attempts ({timeout_seconds:.2f} seconds)."
            )
            try:
                final_desc_response = await asyncio.to_thread(
                    client.describe_statement, Id=statement_id
                )
                final_status = final_desc_response.get("Status", "UNKNOWN")
                final_error = final_desc_response.get("Error", "")
                logger.error(
                    f"Final status on timeout for {statement_id}: {final_status}. Error: {final_error}"
                )
            except Exception as final_desc_err:
                logger.error(
                    f"Could not get final status for timed-out statement {statement_id}: {final_desc_err}"
                )

            raise DataApiTimeoutError(
                f"Timed out after {timeout_seconds:.2f} seconds waiting for statement {statement_id} to complete."
            )

        if desc_response.get("HasResultSet"):
            logger.debug(f"Statement {statement_id} has result set. Fetching...")
            all_records: List[Dict[str, Any]] = []
            next_token: Optional[str] = None
            page_num: int = 0
            while True:
                page_num += 1
                get_result_kwargs: Dict[str, str] = {"Id": statement_id}
                if next_token:
                    get_result_kwargs["NextToken"] = next_token

                logger.debug(
                    f"Fetching result page {page_num} for statement {statement_id}"
                )
                result_response: Dict[str, Any] = await asyncio.to_thread(
                    client.get_statement_result, **get_result_kwargs
                )

                column_metadata: List[Dict[str, Any]] = result_response.get(
                    "ColumnMetadata", []
                )
                records: List[List[Dict[str, Any]]] = result_response.get("Records", [])
                column_names: List[str] = [meta["name"] for meta in column_metadata]

                for record in records:
                    row_dict: Dict[str, Any] = {}
                    for i, col_value in enumerate(record):
                        col_name: str = column_names[i]
                        if col_value.get("isNull", False):
                            row_dict[col_name] = None
                        elif "stringValue" in col_value:
                            row_dict[col_name] = col_value["stringValue"]
                        elif "longValue" in col_value:
                            row_dict[col_name] = col_value["longValue"]
                        elif "doubleValue" in col_value:
                            row_dict[col_name] = col_value["doubleValue"]
                        elif "booleanValue" in col_value:
                            row_dict[col_name] = col_value["booleanValue"]
                        elif "blobValue" in col_value:
                            row_dict[col_name] = (
                                f"<blob len={len(col_value['blobValue'])}>"
                            )
                        else:
                            logger.warning(
                                f"Unhandled value type in column '{col_name}' for statement {statement_id}: {col_value}"
                            )
                            row_dict[col_name] = None
                    all_records.append(row_dict)

                next_token = result_response.get("NextToken")
                if not next_token:
                    break

            logger.info(
                f"Fetched {len(all_records)} records for statement {statement_id}."
            )
            logger.debug(
                f"DEBUG: Returning {len(all_records)} records for statement {statement_id}. First 5: {all_records[:5]}"
            )
            return {"rows": all_records, "error": None}
        else:
            logger.info(f"Statement {statement_id} has no result set.")
            return {"rows": [], "error": None}

    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        logger.error(
            f"Error during Data API execution for SQL '{sql[:100]}...': {error_type} - {error_message}",
            exc_info=True,
        )
        return {"rows": [], "error": f"{error_type}: {error_message}"}
