import re

from django.conf import settings
from django.db.models import Q
from dynamic_preferences.registries import global_preferences_registry

from ..models import Source


def is_sender_allowed(from_email: str, whitelisted_emails: list[str], admin_mails: list[str]) -> bool:
    if from_email in admin_mails:
        return True
    for whitelisted_email in whitelisted_emails:
        if re.search(whitelisted_email, from_email):
            return True
    return False


def handle_inbound(sender, event, esp_name, **kwargs):
    spam_detected = False
    if (message := event.message) and (from_email := message.from_email.addr_spec) and (subject := message.subject):
        if spam_score := getattr(settings, "WBIMPORT_EXPORT_MAILBACKEND_SPAMSCORE", None):
            spam_detected = message.spam_detected or message.spam_score >= spam_score
        if not spam_detected:
            admin_emails = global_preferences_registry.manager()["io__administrator_mails"].split(";")
            conditions = Q(import_parameters__inbound_address__isnull=True)
            for t in message.to:
                conditions |= Q(import_parameters__inbound_address__contains=t.addr_spec)

            sources = Source.objects.filter(
                conditions
                & Q(data_backend__backend_class_path="wbcore.contrib.io.import_export.backends.mail")
                & Q(is_active=True)
            )
            if s := re.search(r"\[([0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\]", subject):
                sources = sources.filter(uuid=s.group(1))
            for source in sources:
                if is_sender_allowed(from_email, source.import_parameters.get("whitelisted_emails", []), admin_emails):
                    source.trigger_workflow(message=message)
