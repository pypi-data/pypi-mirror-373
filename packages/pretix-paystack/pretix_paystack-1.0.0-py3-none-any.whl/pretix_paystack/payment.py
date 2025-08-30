import hashlib
import hmac
import json
import logging
import requests
from collections import OrderedDict
from decimal import Decimal
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin

from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from pretix.base.decimal import round_decimal
from pretix.base.models import Event, OrderPayment, OrderRefund
from pretix.base.payment import BasePaymentProvider, PaymentException
from pretix.base.settings import SettingsSandbox
from pretix.multidomain.urlreverse import eventreverse

logger = logging.getLogger(__name__)


class PaystackSettingsHolder(BasePaymentProvider):
    identifier = 'paystack'
    verbose_name = _('Paystack')
    public_name = _('Card, M-Pesa & Mobile Money via Paystack')

    def __init__(self, event: Event):
        super().__init__(event)
        self.settings = SettingsSandbox('payment', 'paystack', event)

    @property
    def test_mode_message(self):
        if self.settings.get('endpoint') == 'sandbox':
            return _('The Paystack plugin is operating in sandbox mode. No money will actually be transferred.')
        return None

    @property
    def settings_form_fields(self):
        fields = [
            ('endpoint',
             forms.ChoiceField(
                 label=_('Endpoint'),
                 initial='live',
                 choices=(
                     ('live', pgettext_lazy('paystack', 'Live')),
                     ('sandbox', pgettext_lazy('paystack', 'Sandbox')),
                 ),
             )),
            ('public_key_live',
             forms.CharField(
                 label=_('Live Public Key'),
                 max_length=200,
                 required=False,
                 help_text=_('Your Paystack live public key')
             )),
            ('secret_key_live',
             forms.CharField(
                 label=_('Live Secret Key'),
                 max_length=200,
                 required=False,
                 widget=forms.PasswordInput(attrs={
                     'autocomplete': 'new-password'
                 }),
                 help_text=_('Your Paystack live secret key')
             )),
            ('public_key_sandbox',
             forms.CharField(
                 label=_('Sandbox Public Key'),
                 max_length=200,
                 required=False,
                 help_text=_('Your Paystack sandbox public key')
             )),
            ('secret_key_sandbox',
             forms.CharField(
                 label=_('Sandbox Secret Key'),
                 max_length=200,
                 required=False,
                 widget=forms.PasswordInput(attrs={
                     'autocomplete': 'new-password'
                 }),
                 help_text=_('Your Paystack sandbox secret key')
             )),
            ('webhook_secret',
             forms.CharField(
                 label=_('Webhook Secret'),
                 max_length=200,
                 required=False,
                 widget=forms.PasswordInput(attrs={
                     'autocomplete': 'new-password'
                 }),
                 help_text=_('Your Paystack webhook secret for signature verification')
             )),
            ('reconciliation_enabled',
             forms.BooleanField(
                 label=_('Enable payment reconciliation'),
                 help_text=_('Enable automatic reconciliation of pending payments via polling'),
                 required=False,
                 initial=True
             )),
            ('reconciliation_interval',
             forms.IntegerField(
                 label=_('Reconciliation interval (minutes)'),
                 help_text=_('How often to check for pending payments (minimum 5 minutes)'),
                 initial=10,
                 min_value=5,
                 required=False
             )),
            ('reconciliation_threshold',
             forms.IntegerField(
                 label=_('Reconciliation threshold (minutes)'),
                 help_text=_('Only reconcile payments older than this threshold'),
                 initial=10,
                 min_value=1,
                 required=False
             )),
            ('supported_channels',
             forms.MultipleChoiceField(
                 label=_('Supported Payment Channels'),
                 help_text=_('Select which payment methods to offer customers'),
                 choices=[
                     ('card', _('Credit/Debit Cards')),
                     ('bank', _('Bank Transfer')),
                     ('ussd', _('USSD')),
                     ('mobile_money', _('Mobile Money (M-Pesa, etc.)')),
                     ('qr', _('QR Code')),
                     ('eft', _('EFT')),
                 ],
                 initial=['card', 'bank', 'mobile_money'],
                 required=False,
                 widget=forms.CheckboxSelectMultiple
             )),
            ('default_channel',
             forms.ChoiceField(
                 label=_('Default Payment Channel'),
                 help_text=_('Primary payment method to display first'),
                 choices=[
                     ('', _('Let customer choose')),
                     ('card', _('Credit/Debit Cards')),
                     ('bank', _('Bank Transfer')),
                     ('ussd', _('USSD')),
                     ('mobile_money', _('Mobile Money (M-Pesa, etc.)')),
                     ('qr', _('QR Code')),
                     ('eft', _('EFT')),
                 ],
                 initial='',
                 required=False
             )),
            ('mpesa_shortcode',
             forms.CharField(
                 label=_('M-Pesa Shortcode (Optional)'),
                 help_text=_('Your M-Pesa business shortcode if using direct M-Pesa integration'),
                 max_length=20,
                 required=False
             )),
        ]
        
        d = OrderedDict(fields + list(super().settings_form_fields.items()))
        
        d.move_to_end('_enabled', False)
        return d

    def settings_form_clean(self, cleaned_data):
        endpoint = cleaned_data.get('endpoint')
        
        if endpoint == 'live':
            if not cleaned_data.get('public_key_live'):
                raise ValidationError(_('Please provide your live public key'))
            if not cleaned_data.get('secret_key_live'):
                raise ValidationError(_('Please provide your live secret key'))
        elif endpoint == 'sandbox':
            if not cleaned_data.get('public_key_sandbox'):
                raise ValidationError(_('Please provide your sandbox public key'))
            if not cleaned_data.get('secret_key_sandbox'):
                raise ValidationError(_('Please provide your sandbox secret key'))
                
        return cleaned_data

    @property
    def public_key(self):
        if self.settings.get('endpoint') == 'sandbox':
            return self.settings.get('public_key_sandbox')
        return self.settings.get('public_key_live')

    @property
    def secret_key(self):
        if self.settings.get('endpoint') == 'sandbox':
            return self.settings.get('secret_key_sandbox')
        return self.settings.get('secret_key_live')

    @property
    def api_base_url(self):
        if self.settings.get('endpoint') == 'sandbox':
            return 'https://api.paystack.co'
        return 'https://api.paystack.co'

    def _make_api_call(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make authenticated API call to Paystack"""
        url = urljoin(self.api_base_url, endpoint)
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            else:
                raise PaymentException(_('Unsupported HTTP method'))
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f'Paystack API call failed: {str(e)}')
            raise PaymentException(_('Payment provider communication failed'))
        except json.JSONDecodeError:
            logger.error('Invalid JSON response from Paystack API')
            raise PaymentException(_('Invalid response from payment provider'))

    def payment_is_valid_session(self, request):
        return (
            request.session.get('payment_paystack_order_secret') and
            request.session.get('payment_paystack_reference')
        )

    def payment_form_render(self, request, total, order=None) -> str:
        template = get_template('pretix_paystack/checkout_payment_form.html')
        ctx = {
            'request': request,
            'event': self.event,
            'settings': self.settings,
            'public_key': self.public_key,
            'total': total,
            'order': order,
        }
        return template.render(ctx)

    def checkout_prepare(self, request, total, order=None):
        """Prepare checkout by initializing Paystack transaction"""
        if not self.public_key or not self.secret_key:
            messages.error(request, _('Payment provider is not properly configured.'))
            return False

        # Generate unique reference
        reference = f"{self.event.slug}-{order.code if order else 'temp'}-{hash(str(total) + str(request.session.session_key))}"
        
        # Store in session for validation
        request.session['payment_paystack_reference'] = reference
        request.session['payment_paystack_order_secret'] = order.secret if order else None
        
        return True

    def payment_perform(self, request, payment: OrderPayment) -> str:
        """Initialize Paystack transaction and return checkout URL or form"""
        try:
            # Get supported channels from settings
            supported_channels = self.settings.get('supported_channels', ['card', 'bank', 'mobile_money'])
            default_channel = self.settings.get('default_channel', '')
            mpesa_shortcode = self.settings.get('mpesa_shortcode', '')
            
            # Initialize transaction with Paystack
            data = {
                'email': payment.order.email,
                'amount': int(payment.amount * 100),  # Convert to kobo/cents
                'reference': f"{self.event.slug}-{payment.order.code}-{payment.local_id}",
                'callback_url': self.get_success_url(payment),
                'channels': supported_channels,  # Specify allowed payment channels
                'metadata': {
                    'order_code': payment.order.code,
                    'event_slug': self.event.slug,
                    'payment_id': payment.local_id,
                    'supported_channels': supported_channels,
                    'default_channel': default_channel,
                    'mpesa_shortcode': mpesa_shortcode if mpesa_shortcode else None,
                    'custom_fields': [
                        {
                            'display_name': 'Event',
                            'variable_name': 'event',
                            'value': str(self.event.name)
                        },
                        {
                            'display_name': 'Order',
                            'variable_name': 'order',
                            'value': payment.order.code
                        }
                    ]
                }
            }
            
            # Add currency-specific settings for M-Pesa
            if 'mobile_money' in supported_channels:
                # For Kenyan Shillings, ensure M-Pesa is properly configured
                if self.event.currency == 'KES' and mpesa_shortcode:
                    data['metadata']['mpesa_configuration'] = {
                        'shortcode': mpesa_shortcode,
                        'currency': 'KES'
                    }
            
            response = self._make_api_call('POST', '/transaction/initialize', data)
            
            if response.get('status') and response.get('data'):
                # Store transaction reference
                payment.info_data = {
                    'paystack_reference': response['data']['reference'],
                    'access_code': response['data']['access_code'],
                    'authorization_url': response['data']['authorization_url']
                }
                payment.save(update_fields=['info'])
                
                # Return redirect URL for Paystack hosted page
                return response['data']['authorization_url']
            else:
                logger.error(f'Paystack transaction initialization failed: {response}')
                raise PaymentException(_('Payment initialization failed'))
                
        except Exception as e:
            logger.error(f'Payment perform error: {str(e)}')
            raise PaymentException(_('Payment could not be processed'))

    def payment_pending_render(self, request, payment: OrderPayment) -> str:
        """Render pending payment page"""
        template = get_template('pretix_paystack/pending.html')
        ctx = {
            'request': request,
            'event': self.event,
            'settings': self.settings,
            'payment': payment,
            'order': payment.order,
        }
        return template.render(ctx)

    def payment_control_render(self, request, payment: OrderPayment) -> str:
        """Render payment details in control panel"""
        template = get_template('pretix_paystack/control.html')
        ctx = {
            'request': request,
            'event': self.event,
            'settings': self.settings,
            'payment': payment,
            'method': 'Paystack',
            'info': payment.info_data,
        }
        return template.render(ctx)

    def get_success_url(self, payment: OrderPayment) -> str:
        """Get success callback URL"""
        return eventreverse(self.event, 'plugins:pretix_paystack:return', kwargs={
            'order': payment.order.code,
            'secret': payment.order.secret,
            'payment': payment.pk,
        })

    def verify_payment(self, reference: str) -> Dict[str, Any]:
        """Verify payment status with Paystack API"""
        try:
            response = self._make_api_call('GET', f'/transaction/verify/{reference}')
            return response
        except Exception as e:
            logger.error(f'Payment verification failed for reference {reference}: {str(e)}')
            raise PaymentException(_('Payment verification failed'))

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Paystack webhook signature"""
        webhook_secret = self.settings.get('webhook_secret')
        if not webhook_secret:
            logger.warning('Webhook secret not configured')
            return False
            
        try:
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha512
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f'Webhook signature verification failed: {str(e)}')
            return False

    def process_webhook_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Process webhook event and update payment status"""
        try:
            reference = data.get('reference')
            if not reference:
                logger.error('Webhook event missing reference')
                return False

            # Find payment by reference
            payment = self._find_payment_by_reference(reference)
            if not payment:
                logger.warning(f'Payment not found for reference: {reference}')
                return False

            if event_type == 'charge.success':
                self._handle_successful_payment(payment, data)
            elif event_type == 'charge.failed':
                self._handle_failed_payment(payment, data)
            elif event_type == 'charge.dispute.create':
                self._handle_disputed_payment(payment, data)
            else:
                logger.info(f'Unhandled webhook event type: {event_type}')
                
            return True
            
        except Exception as e:
            logger.error(f'Webhook processing failed: {str(e)}')
            return False

    def _find_payment_by_reference(self, reference: str) -> Optional[OrderPayment]:
        """Find payment by Paystack reference"""
        try:
            return OrderPayment.objects.get(
                provider=self.identifier,
                info__contains=reference
            )
        except OrderPayment.DoesNotExist:
            return None
        except OrderPayment.MultipleObjectsReturned:
            logger.error(f'Multiple payments found for reference: {reference}')
            return None

    def _handle_successful_payment(self, payment: OrderPayment, data: Dict[str, Any]):
        """Handle successful payment webhook"""
        if payment.state in (OrderPayment.PAYMENT_STATE_CONFIRMED, OrderPayment.PAYMENT_STATE_REFUNDED):
            logger.info(f'Payment {payment.pk} already processed')
            return

        # Update payment info with Paystack data
        payment.info_data.update({
            'paystack_transaction_id': data.get('id'),
            'paystack_status': data.get('status'),
            'paystack_gateway_response': data.get('gateway_response'),
            'paystack_paid_at': data.get('paid_at'),
            'paystack_channel': data.get('channel'),
            'paystack_currency': data.get('currency'),
            'paystack_amount': data.get('amount'),
        })
        
        try:
            payment.confirm()
            logger.info(f'Payment {payment.pk} confirmed via webhook')
        except Exception as e:
            logger.error(f'Failed to confirm payment {payment.pk}: {str(e)}')

    def _handle_failed_payment(self, payment: OrderPayment, data: Dict[str, Any]):
        """Handle failed payment webhook"""
        if payment.state == OrderPayment.PAYMENT_STATE_CANCELED:
            logger.info(f'Payment {payment.pk} already canceled')
            return

        # Update payment info
        payment.info_data.update({
            'paystack_transaction_id': data.get('id'),
            'paystack_status': data.get('status'),
            'paystack_gateway_response': data.get('gateway_response'),
            'paystack_channel': data.get('channel'),
        })
        
        try:
            payment.fail(info=data.get('gateway_response', 'Payment failed'))
            logger.info(f'Payment {payment.pk} marked as failed via webhook')
        except Exception as e:
            logger.error(f'Failed to mark payment {payment.pk} as failed: {str(e)}')

    def _handle_disputed_payment(self, payment: OrderPayment, data: Dict[str, Any]):
        """Handle disputed payment webhook"""
        payment.info_data.update({
            'paystack_dispute_id': data.get('id'),
            'paystack_dispute_status': data.get('status'),
            'paystack_dispute_reason': data.get('reason'),
        })
        payment.save(update_fields=['info'])
        
        logger.warning(f'Payment {payment.pk} disputed: {data.get("reason")}')

    def payment_refund_supported(self, payment: OrderPayment) -> bool:
        """Check if refund is supported for this payment"""
        return (
            payment.state == OrderPayment.PAYMENT_STATE_CONFIRMED and
            payment.info_data.get('paystack_transaction_id')
        )

    def payment_partial_refund_supported(self, payment: OrderPayment) -> bool:
        """Check if partial refund is supported"""
        return self.payment_refund_supported(payment)

    def execute_refund(self, refund: OrderRefund):
        """Execute refund via Paystack API"""
        payment = refund.payment
        transaction_id = payment.info_data.get('paystack_transaction_id')
        
        if not transaction_id:
            raise PaymentException(_('Cannot refund payment without transaction ID'))

        try:
            data = {
                'transaction': transaction_id,
                'amount': int(refund.amount * 100),  # Convert to kobo/cents
                'merchant_note': f'Refund for order {payment.order.code}',
            }
            
            response = self._make_api_call('POST', '/refund', data)
            
            if response.get('status') and response.get('data'):
                refund.info_data = {
                    'paystack_refund_id': response['data']['id'],
                    'paystack_transaction_id': response['data']['transaction']['id'],
                    'paystack_status': response['data']['status'],
                }
                refund.done()
                logger.info(f'Refund {refund.pk} processed successfully')
            else:
                logger.error(f'Paystack refund failed: {response}')
                raise PaymentException(_('Refund processing failed'))
                
        except Exception as e:
            logger.error(f'Refund execution failed: {str(e)}')
            raise PaymentException(_('Refund could not be processed'))
