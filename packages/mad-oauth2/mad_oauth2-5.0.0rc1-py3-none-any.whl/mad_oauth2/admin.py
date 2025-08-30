import logging

from django.contrib import admin
from oauth2_provider.admin import ApplicationAdmin

from mad_oauth2.models import Scope
from mad_oauth2.models import Throttle

logger = logging.getLogger(__name__)

# Register your models here.


class ApplicationAdminClass(ApplicationAdmin):
    filter_horizontal = ("scopes",)
    readonly_fields = ["id"]
    list_display = [
        "id",
        "name",
        "client_type",
        "authorization_grant_type",
        "created_at",
    ]


@admin.register(Scope)
class ScopeAdminClass(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = [
        "id",
        "name",
        "key",
    ]


@admin.register(Throttle)
class ThrottleAdminClass(admin.ModelAdmin):
    readonly_fields = ["id"]
    list_display = ["id", "name", "rate", "application"]
    filter_horizontal = ("scopes",)
