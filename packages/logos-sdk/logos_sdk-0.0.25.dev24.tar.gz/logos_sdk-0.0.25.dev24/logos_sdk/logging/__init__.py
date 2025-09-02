from logos_sdk.logging.LogosLogger import LogosLogger
import logging

# log types in labels
NOTIFICATION = "notification"
DEBUG = "debug"
RESULT = "result"
RESULT_UI_ONLY = "result-ui-only"


def setup_from_request(request, logger_name="logos-logging"):
    # We want to parse as much as possible without raising an exception.
    # we want to be able to at least create a complete notification log, for this we need labels without accesses and trace.
    try:
        trace = request.headers["X-Cloud-Trace-Context"]
    except Exception as err:
        raise Exception(f"Unable to retrieve trace from request ({err})")

    try:
        logger = LogosLogger(logger_name, {}, trace)
    except Exception as err:
        raise Exception(f"Unable to ser up LogosLogger ({err})")

    try:
        body = request.get_json()
    except Exception as err:
        message = f"Unable to parse request body as a valid json ({err})"
        logger.log(
            message=message,
            severity=logging.ERROR,
            log_type=NOTIFICATION,
        )
        raise Exception(message)

    try:
        labels = {
            "id": str(body["id"]),
            "client": str(body["client"]),
            "script": str(body["script"]),
            "author": str(body["author"]),
        }
        logger.labels = labels
    except Exception as err:
        message = f"Unable to create labels, missing key ({err})"
        logger.log(
            message=message,
            severity=logging.ERROR,
            log_type=NOTIFICATION,
        )
        raise Exception(message)

    # To run the script itself, we need the rest. If we are not able to run it,
    # we want to be able to at least create a complete notification log.
    try:
        settings = body["settings"]
        logger.settings = body["settings"]
    except Exception as err:
        message = f"Missing required settings ({err})"
        logger.log(
            message=message,
            severity=logging.ERROR,
            log_type=NOTIFICATION,
        )
        raise Exception(message)

    try:
        accesses = {
            str(access["platform"]["short_name"]): str(
                access["account"]["account_platform_id"]
            )
            for access in body["accesses"]
        }
        labels = {**labels, **accesses}
        logger.labels = labels
        logger.accesses = body["accesses"]
    except Exception as err:
        message = f"Unable to parse accesses ({err})"
        logger.log(
            message=message,
            severity=logging.ERROR,
            log_type=NOTIFICATION,
        )
        raise Exception(message)

    try:
        secrets = {
            str(access["platform"]["short_name"]): str(access["secret"]["name"])
            for access in body["accesses"]
        }
    except Exception as err:
        message = f"Unable to parse secrets ({err})"
        logger.log(
            message=message,
            severity=logging.ERROR,
            log_type=NOTIFICATION,
        )
        raise Exception(message)

    return logger, labels, settings, secrets
