from celery import shared_task
from oauth2_provider.models import get_access_token_model, get_refresh_token_model
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(name="Periodic: Remove Expired Tokens")
def removeExpiredTokens():
    """_summary_

    Returns:
        _type_: _description_
    """
    try:
        get_access_token_model().objects.filter(expires__lt=timezone.now()).delete()
        return "Expired token clean up completed successfully."
    except Exception as e:
        logger.error("Error deleting Expired Tokens: " + str(e))
        return "Error: " + str(e)


@shared_task(name="Periodic: Remove Revoked Refresh Tokens")
def remove_revoked_refresh_tokens():
    """_summary_

    Returns:
        _type_: _description_
    """
    try:
        get_refresh_token_model().objects.filter(revoked__lt=timezone.now()).delete()
        return "Revoked Refresh token clean up completed successfully."
    except Exception as e:
        logger.error("Error deleting Expired Tokens: " + str(e))
        return "Error: " + str(e)
