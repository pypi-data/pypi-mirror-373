from oauth2_provider.scopes import BaseScopes

from mad_oauth2.models import Scope


class ApplicationScopes(BaseScopes):
    def get_all_scopes(self):
        r = {}
        scopes = Scope.objects.values("key", "name")
        for scope in scopes:
            r[scope["key"]] = scope["name"]
        return r

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        return list(Scope.objects.values_list("key", flat=True))

    def get_default_scopes(self, application, request=None, *args, **kwargs):
        """these scopes will be set on the access token if they are found in get_available_scopes()"""
        return list(application.allowed_scopes.values_list("key", flat=True))
