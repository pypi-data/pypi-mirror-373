# Datadog for DBTP hosted Django applications

Instrument Django applications running in DBTP (AWS Copilot/Fargate).

For more information see: https://ddtrace.readthedocs.io/en/stable/integrations.html#django

## Prerequisits

Your service needs the Datadog agent sidecar. See: https://platform.readme.trade.gov.uk/next-steps/observability/datadog/enable-datadog-for-your-application/

## Setup

1. Install: `pip install dbt-django-datadog`

2. Add `datadog` to settings.INSTALLED_APPS

3. Add `datadog.middleware.DatadogMiddleware` to settings.MIDDLEWARE

## Contributing

If you would like to contribute, raise a pull request and ask the SRE team for a code review.
