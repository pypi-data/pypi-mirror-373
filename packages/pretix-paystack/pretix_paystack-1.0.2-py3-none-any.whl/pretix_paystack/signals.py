from django.dispatch import receiver
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from pretix.base.signals import register_payment_providers, register_global_settings
from pretix.presale.signals import process_response


@receiver(register_payment_providers, dispatch_uid="payment_paystack")
def register_payment_provider(sender, **kwargs):
    from .payment import PaystackSettingsHolder
    return PaystackSettingsHolder


@receiver(signal=process_response, dispatch_uid="payment_paystack_middleware")
def signal_process_response(sender, request, response, **kwargs):
    from .urls import event_patterns
    sender.patterns = getattr(sender, 'patterns', []) + [
        path('_paystack/', include((event_patterns, 'pretix_paystack'))),
    ]
    return response
