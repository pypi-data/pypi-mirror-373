import json
from asgiref.sync import iscoroutinefunction, sync_to_async

from ddtrace import tracer


def sanitise_data(data):
    sensitive_keys = {"password", "secret", "token", "api_key", "name", "username", "email", "first_name", "last_name", "givenname", "forename", "address"}
    if isinstance(data, dict):
        return {
            k: "***" if k.lower() in sensitive_keys else sanitise_data(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [sanitise_data(item) for item in data]
    return data


def truncate_body(body, max_length=512):
    if len(body) > max_length:
        return body[:max_length] + "... [truncated]"
    return body


def get_safe_body(request):
    try:
        return request.body.decode("utf-8")
    except UnicodeDecodeError:
        return f"<binary body: {len(request.body)} bytes>"


class DatadogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.is_async = iscoroutinefunction(self.get_response)
        self.tracer = tracer

    def _sync_process_request(self, request):
        span = self.tracer.current_root_span()

        if not span:
            span = self.tracer.trace("django.datadog")

        cookies = {k: v for k, v in request.COOKIES.items()}
        sanitised_cookies = sanitise_data(cookies)
        span.set_tag("http.cookies", json.dumps(sanitised_cookies, default=str))

        if request.method in ("POST", "PUT", "PATCH") and request.body:
            try:
                content_type = request.content_type.lower()
                if "json" in content_type:
                    body_data = json.loads(request.body)
                    sanitised_body = sanitise_data(body_data)
                    body_str = json.dumps(sanitised_body)
                elif "form" in content_type:
                    body_data = request.POST.dict()
                    sanitised_body = sanitise_data(body_data)
                    body_str = json.dumps(sanitised_body)
                else:
                    body_str = get_safe_body(request)

                truncated_body = truncate_body(body_str)
                span.set_tag("http.request_body", truncated_body)
            except Exception as e:
                span.set_tag("http.request_body_error", str(e))

        return None

    async def _async_process_request(self, request):
        return await sync_to_async(self._sync_process_request)(request)

    def __call__(self, request):
        self._sync_process_request(request)
        response = self.get_response(request)
        return response

    async def __acall__(self, request):
        await self._async_process_request(request)
        response = await self.get_response(request)
        return response
