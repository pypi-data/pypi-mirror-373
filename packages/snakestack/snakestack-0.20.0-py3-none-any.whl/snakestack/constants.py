# Unidades de tamanho
KILOBYTE = 1024
MEGABYTE = 1024 * 1024
GIGABYTE = 1024 * 1024 * 1024
TERABYTE = 1024 * 1024 * 1024 * 1024

# Unidades de tempo
MILLISECONDS = 0.001
SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES

# Docs
ERROR_DETAIL_SCHEMA_DESCRIPTION = "Error message or explanation"
PAGINATE_LIMIT_SCHEMA_DESCRIPTION = "The maximum number of items to return per page."
PAGINATE_OFFSET_SCHEMA_DESCRIPTION = (
    "The number of items to skip before starting "
    "to collect the result set."
)
PAGINATE_TOTAL_PAGES_SCHEMA_DESCRIPTION = (
    "Total number of pages based on total items and page size."
)
PAGINATE_HAS_PREV_SCHEMA_DESCRIPTION = (
    "Indicates if there is a previous page available."
)
PAGINATE_HAS_NEXT_SCHEMA_DESCRIPTION = "Indicates if there is a next page available."
PAGINATE_SIZE_SCHEMA_DESCRIPTION = (
    "Total number of pages based on total items and page size."
)
PAGINATE_PAGE_SCHEMA_DESCRIPTION = "Current page number, starting at 1."
PAGINATE_TOTAL_SCHEMA_DESCRIPTION = "Total number of data available in the database."
PAGINATE_ITEMS_SCHEMA_DESCRIPTION = "List of resources returned in the current page."

SCHEMA_CHECK_OK_DESCRIPTION = (
    "Indicates whether the individual "
    "check passed successfully."
)
SCHEMA_CHECK_LATENCY_MS_DESCRIPTION = (
    "Latency in milliseconds for the check to complete."
)
SCHEMA_CHECK_ERROR_DESCRIPTION = (
    "Error message if the check failed; null if successful."
)
SCHEMA_HEALTHZ_SERVICE_NAME_DESCRIPTION = (
    "Name of the service responding to the ping request."
)
SCHEMA_HEALTHZ_VERSION_DESCRIPTION = (
    "Version of the deployed service or application."
)
SCHEMA_HEALTHZ_HOST_DESCRIPTION = (
    "Hostname or identifier of the running instance."
)
SCHEMA_HEALTHZ_UPTIME_DESCRIPTION = (
    "Formatted uptime of the service (e.g., '2d 4h')."
)
SCHEMA_HEALTHZ_TIMESTAMP_DESCRIPTION = "Current timestamp in ISO format."
SCHEMA_HEALTHZ_ENVIRONMENT_DESCRIPTION = (
    "Environment the service is running in (e.g., 'production', 'staging')."
)
SCHEMA_HEALTHZ_STATUS_DESCRIPTION = "Overall health status. True if all checks passed."
SCHEMA_HEALTHZ_LATENCY_MS_DESCRIPTION = (
    "Total time taken to run all health checks."
)
SCHEMA_HEALTHZ_DETAILS_DESCRIPTION = (
    "Breakdown of each individual check by name."
)
