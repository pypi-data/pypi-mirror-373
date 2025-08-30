from oauth2_provider.models import AccessToken

from mad_oauth2.models import Throttle
from mad_oauth2.settings import oauth2_settings


def get_application_from_request(request):
    """Extract application from the request's authorization token."""
    if not request.auth:
        return None

    try:
        # Assuming request.auth is the token string
        token = AccessToken.objects.select_related("application").get(
            token=request.auth
        )
        return token.application  # noqa: TRY300
    except (AccessToken.DoesNotExist, AttributeError):
        return None


class ThrottleClass:
    def __init__(self):
        self.scope_rates = {}
        self.app_scope_rates = {}

        # Retrieve all throttles and their associated scopes
        throttles = Throttle.objects.prefetch_related("scopes").all()

        # For each throttle, apply its rate to all its scopes
        for throttle in throttles:
            for scope in throttle.scopes.all():
                # Store general scope rates
                if throttle.application is None:
                    self.scope_rates[scope.key] = throttle.rate
                # Store application-specific scope rates
                else:
                    app_id = throttle.application.id
                    if app_id not in self.app_scope_rates:
                        self.app_scope_rates[app_id] = {}
                    self.app_scope_rates[app_id][scope.key] = throttle.rate

    def get_throttling_rates(self, application=None):
        """
        Get throttling rates for a specific application or default rates.

        Args:
            application: The OAuth2 application or None for default rates

        Returns:
            Dictionary of scope keys to throttle rates
        """
        if application and application.id in self.app_scope_rates:
            # Merge default rates with application-specific rates
            rates = self.scope_rates.copy()
            rates.update(self.app_scope_rates[application.id])
            return rates
        return self.scope_rates


def get_throttling(application=None):
    throttling = oauth2_settings.THROTTLE_CLASS()
    return throttling.get_throttling_rates(application)
