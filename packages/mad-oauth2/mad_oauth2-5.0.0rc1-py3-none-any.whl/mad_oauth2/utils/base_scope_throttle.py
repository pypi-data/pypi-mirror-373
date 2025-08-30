from rest_framework.throttling import SimpleRateThrottle

from mad_oauth2.throttling import get_application_from_request
from mad_oauth2.throttling import get_throttling


class BaseScopedRateThrottle(SimpleRateThrottle):
    scope_attr = "throttle_scope"

    def __init__(self):
        # Initialize without rate to avoid errors
        self.rate = None
        self.num_requests = None
        self.duration = None

    def allow_request(self, request, view):
        # We can only determine the scope once we're called by the view.
        self.scope = getattr(view, self.scope_attr, None)

        # If a view does not have a `throttle_scope` always allow the request
        if not self.scope:
            return True

        # Get the application from the request
        application = get_application_from_request(request)

        # Get throttling rates for this application (or default rates)
        throttle_rates = get_throttling(application)

        # Get the rate for this specific scope
        self.rate = throttle_rates.get(self.scope)

        # If no rate is set for this scope, allow the request
        if not self.rate:
            return True

        # Parse the rate string
        self.num_requests, self.duration = self.parse_rate(self.rate)

        # We can now proceed as normal.
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        """
        Generate the unique cache key by concatenating the user id or client id
        with the '.throttle_scope` property of the view.
        """
        if request.user is not None and request.user.is_authenticated:
            ident = f"user_{request.user.pk}"
        else:
            application = get_application_from_request(request)
            ident = f"app_{application.id}" if application else self.get_ident(request)

        return self.cache_format % {"scope": self.scope, "ident": ident}
