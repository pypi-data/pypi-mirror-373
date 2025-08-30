"""Utilities for monitoring and observability integration.

This module provides utilities for integrating with monitoring and observability tools
like NewRelic. It handles availability checking and provides wrapper functions that
conditionally use monitoring tools only when they're available and properly initialized.

NOTE: NewRelic is an optional dependency. To use monitoring functionality, install
the package with the monitoring extras:
    pip install futurehouse-client[monitoring]

Environment variables:
    NEW_RELIC_ENVIRONMENT: The environment to use for NewRelic reporting (dev, staging, prod)
    NEW_RELIC_CONFIG_FILE: Path to the NewRelic configuration file
    NEW_RELIC_LICENSE_KEY: Your NewRelic license key
"""

import contextlib
import json
import logging
import os
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# Check if NewRelic initialization is enabled (default: False)
NEWRELIC_AUTO_INIT = (
    os.environ.get("FUTUREHOUSE_NEWRELIC_AUTO_INIT", "false").lower() == "true"
)

# Check if NewRelic is installed
try:
    import newrelic.agent

    NEWRELIC_INSTALLED = True
except ImportError:
    NEWRELIC_INSTALLED = False
    logger.info("NewRelic package not installed")

# Context variable to track NewRelic initialization state
newrelic_initialized: ContextVar[bool] = ContextVar(
    "newrelic_initialized", default=False
)


def ensure_newrelic() -> bool:  # noqa: PLR0911
    """Check if NewRelic is available and initialize it if auto-init is enabled.

    This will use environment variables:
    - FUTUREHOUSE_NEWRELIC_AUTO_INIT: Set to "true" to enable automatic initialization (default: "false")
    - NEW_RELIC_CONFIG_FILE: Path to the NewRelic config file (required)
    - NEW_RELIC_ENVIRONMENT: Environment (dev, staging, prod)

    Returns:
        bool: True if NewRelic is available for use, False otherwise
    """
    if newrelic_initialized.get():
        return True

    if not NEWRELIC_AUTO_INIT:
        return False

    if not NEWRELIC_INSTALLED:
        logger.info("NewRelic package is not installed")
        return False

    nr_config = os.environ.get("NEW_RELIC_CONFIG_FILE")
    if not nr_config:
        logger.warning("NEW_RELIC_CONFIG_FILE environment variable must be set")
        return False

    try:
        nr_env = os.environ.get("NEW_RELIC_ENVIRONMENT", "dev")
        newrelic.agent.initialize(nr_config, environment=nr_env)

        app = newrelic.agent.application()
        if app is None:
            logger.warning("NewRelic initialization failed: no application returned")
            return False

        newrelic_initialized.set(True)
        logger.info(f"NewRelic initialized successfully for environment: {nr_env}")
    except Exception as e:
        logger.warning(f"NewRelic initialization failed: {e}")
        return False

    else:
        return True


def insert_distributed_trace_headers(headers: dict[str, str]) -> dict[str, str]:
    """Insert distributed trace headers if NewRelic is available.

    Args:
        headers: The headers dictionary to modify.

    Returns:
        The modified headers dictionary with NewRelic distributed trace headers if available,
        otherwise the original headers.
    """
    if not ensure_newrelic():
        return headers

    try:
        nr_headers: list[tuple[str, str]] = []
        newrelic.agent.insert_distributed_trace_headers(nr_headers)
        for header in nr_headers:
            headers[header[0]] = header[1]
    except Exception as e:
        logger.info(f"Error inserting distributed trace headers: {e}")

    return headers


@contextlib.contextmanager
def external_trace(
    url: str,
    method: str = "GET",
    library: str = "httpx",
    custom_params: dict | None = None,
):
    """Context manager for NewRelic external traces that works whether NewRelic is available or not.

    Creates an ExternalTrace span in NewRelic for HTTP requests to external services. This provides detailed timing and proper distributed tracing between services.
    "External" refers to HTTP requests made to services outside of your application (like third-party APIs or other microservices).

    Args:
        url: The URL being called.
        method: The HTTP method (GET, POST, etc.).
        library: The library being used for the HTTP call.
        custom_params: Optional dictionary of custom parameters to add to the transaction.

    Yields:
        None: This is a context manager that doesn't yield a value.
    """
    if not ensure_newrelic():
        yield
        return

    # Proceed with tracing
    try:
        with newrelic.agent.ExternalTrace(
            library=library,
            url=url,
            method=method,
        ):
            txn = newrelic.agent.current_transaction()
            if txn:
                txn.add_custom_parameter("request_url", url)
                txn.add_custom_parameter("request_method", method)

                if custom_params:
                    for key, value in custom_params.items():
                        txn.add_custom_parameter(key, value)

            yield
    except Exception as e:
        # If there's an exception in the transaction handling,
        # log it but don't let it break the client
        try:
            txn = newrelic.agent.current_transaction()
            if txn:
                txn.add_custom_parameter("external_request_url", url)
                txn.add_custom_parameter("external_request_method", method)
                txn.add_custom_parameter("error_type", e.__class__.__name__)
                txn.add_custom_parameter("error_message", str(e))
                txn.record_exception(e)
        except Exception as nr_error:
            # If even the error handling fails, just log it
            logger.info(f"Failed to record NewRelic error: {nr_error}")

        # Always re-raise the original exception
        raise


@contextlib.contextmanager
def monitored_transaction(
    name: str, group: str = "Task", custom_params: dict | None = None
):
    """Context manager for NewRelic transactions that appear in distributed traces.

    This uses WebTransaction for better visibility in distributed traces, even for
    background job-type workloads.

    Args:
        name: Name of the transaction (e.g., 'run_crow_job')
        group: Group for transaction categorization (default: 'Task')
        custom_params: Optional dictionary of custom parameters to add to the transaction

    Yields:
        None: This is a context manager that doesn't yield a value.
    """
    if not ensure_newrelic():
        logger.info("NewRelic not available, skipping transaction")
        yield
        return

    try:
        app = newrelic.agent.application()
        if app is None:
            logger.warning("No NewRelic application found, skipping transaction")
            yield
            return

        parsed_headers = None
        trace_context = os.environ.get("NEW_RELIC_DISTRIBUTED_TRACING_CONTEXT")
        if trace_context:
            try:
                parsed_headers = json.loads(trace_context)
            except Exception as e:
                logger.warning(f"Failed to parse distributed trace context: {e}")
        else:
            logger.info("No distributed trace context found")

        with newrelic.agent.WebTransaction(app, name, group=group):
            if parsed_headers:
                current_txn = newrelic.agent.current_transaction()
                if current_txn:
                    accepted = newrelic.agent.accept_distributed_trace_headers(
                        parsed_headers
                    )
                    if not accepted:
                        logger.warning("Failed to accept distributed trace headers")

            if custom_params:
                txn = newrelic.agent.current_transaction()
                if txn:
                    for key, value in custom_params.items():
                        txn.add_custom_parameter(key, value)

            yield
            logger.info(f"Completed NewRelic transaction: {name}")
    except Exception as e:
        # If there's an exception in the transaction handling,
        # log it but don't let it break the client
        try:
            txn = newrelic.agent.current_transaction()
            if txn:
                txn.add_custom_parameter("error_type", e.__class__.__name__)
                txn.add_custom_parameter("error_message", str(e))
                txn.record_exception(e)
        except Exception as nr_error:
            # If even the error handling fails, just log it
            logger.info(f"Failed to record NewRelic error: {nr_error}")

        logger.warning(f"Error in NewRelic transaction: {e}")
        yield
