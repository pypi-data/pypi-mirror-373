from random import randint

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from oauth2_provider.models import AbstractApplication
from oauth2_provider.settings import oauth2_settings

# Create your models here.


class Scope(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    key = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        unique=True,
        help_text="View name, must match a valid name in View, see documentation.",
    )
    description = models.TextField(  # noqa: DJ001
        blank=True,
        null=True,
        help_text="Detailed Description for this scope you might want show to the user.",  # noqa: E501
    )
    admin_note = models.TextField(blank=True, null=True)  # noqa: DJ001

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return str(self.name) + " - " + str(self.key)


class Throttle(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    rate = models.CharField(
        max_length=255,
        default="100/day",
        blank=False,
        null=False,
        help_text="Example: 100/day</br>Options: sec, min, hour, day",
    )
    scope = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="If you have scope 'user:read' and 'user:write', scope here should be 'user' and it will throttle both.",  # noqa: E501
    )
    scopes = models.ManyToManyField(
        Scope,
        related_name="throttles",
        help_text="Scopes that this throttle rate applies to.",
    )
    application = models.ForeignKey(
        oauth2_settings.APPLICATION_MODEL, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return str(self.name)


class Oauth2ApplicationAbstract(AbstractApplication):
    namespace = models.CharField(max_length=255, blank=True, null=True, unique=True)
    scopes = models.ManyToManyField(
        Scope, related_name="%(app_label)s_%(class)s_scopes"
    )
    allowed_schemes = models.TextField(  # noqa: DJ001
        _("Allowed Schemes"),
        blank=True,
        null=True,
        help_text="list of allowed schemes, seperated by new line.",
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-id"]
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self):
        return str(self.id) + " - " + str(self.name)

    def save(self, *args, **kwargs):
        if self.namespace is None or self.namespace == "":
            self.namespace = slugify(self.name)
        else:
            self.namespace = slugify(self.namespace)

        if self._state.adding is True:
            self.namespace = self.namespace + "-" + str(randint(0, 9999999))  # noqa: S311

        super().save(*args, **kwargs)

    def get_allowed_schemes(self):
        if self.allowed_schemes is None or self.allowed_schemes == "":
            return super().get_allowed_schemes()
        # get content seperated by new line and convert to list
        return self.allowed_schemes.splitlines()

    @property
    def allowed_scopes(self):
        return self.scopes


class Application(Oauth2ApplicationAbstract):
    pass
