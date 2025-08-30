from rest_framework.throttling import SimpleRateThrottle

from mad_oauth2.throttling import get_application_from_request
from mad_oauth2.throttling import get_throttling


class ApplicationBaseScopedRateThrottle(SimpleRateThrottle):
    scope_attr = "required_alternate_scopes"

    def __init__(self):
        self.request = None
        self.application = None
        self.throttle_rates = None

    def allow_request(self, request, view):
        self.request = request
        # We can only determine the scope once we're called by the view.
        view_scopes = getattr(view, self.scope_attr, None)
        if not view_scopes:
            return True

        # Determine the scope based on the request method
        request_method = request.method.upper()
        method_scopes = view_scopes.get(request_method, [])

        # If a view does not have a `throttle_scope` always allow the request
        if not method_scopes:
            return True

        # Flatten the scopes and find the first matching throttle rate
        all_scopes = [
            scope for sublists in method_scopes for item in sublists for scope in [item]
        ]

        # Get the application from the request
        application = get_application_from_request(request)

        # Get throttling rates for this application (or default rates)
        throttle_rates = get_throttling(application)

        # Find the first scope with a defined throttle rate
        matching_scopes = [scope for scope in all_scopes if scope in throttle_rates]

        # If no scopes have a defined rate, allow the request
        if not matching_scopes:
            return True

        # Use the first matching scope's rate
        self.scope = matching_scopes[0]
        self.rate = throttle_rates.get(self.scope)

        self.num_requests, self.duration = self.parse_rate(self.rate)

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
