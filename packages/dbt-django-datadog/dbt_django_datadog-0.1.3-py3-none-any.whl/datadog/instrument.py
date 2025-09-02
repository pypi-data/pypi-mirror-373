from django.conf import settings


def _instrument():
    # this applies datadog
    import ddtrace.auto


def configure_datadog():
    """Instrument the app for Datadog applying the default DBT config"""
    import ddtrace
    config = ddtrace.config

    # additional options that can only be configured this way - they're not availble if we use ddtrace-run
    config.django["trace_fetch_methods"] = True  # include the method names
    config.django["trace_query_string"] = True  # include the trace query string

    database_name = getattr(settings, "DATABASES", {}).get("default", {}).get("NAME")
    if database_name:
        config.django["database_service_name"] = database_name

    _instrument()
