import hashlib
import hmac
import json
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from django.test import TestCase, RequestFactory
from django.utils.timezone import now

from pretix.base.models import Event, Organizer, Order, OrderPayment
from pretix.base.payment import PaymentException
from pretix_paystack.payment import PaystackSettingsHolder


class PaystackPaymentTest(TestCase):
    def setUp(self):
        self.organizer = Organizer.objects.create(name='Test Organizer', slug='test-org')
        self.event = Event.objects.create(
            organizer=self.organizer,
            name='Test Event',
            slug='test-event',
            date_from=now(),
            currency='NGN'
        )
        self.order = Order.objects.create(
            code='TEST123',
            event=self.event,
            email='test@example.com',
            status=Order.STATUS_PENDING,
            total=Decimal('100.00')
        )
        self.payment = OrderPayment.objects.create(
            order=self.order,
            provider='paystack',
            amount=Decimal('100.00'),
            state=OrderPayment.PAYMENT_STATE_CREATED
        )
        
        # Configure test settings
        self.provider = PaystackSettingsHolder(self.event)
        self.provider.settings.set('endpoint', 'sandbox')
        self.provider.settings.set('public_key_sandbox', 'pk_test_123')
        self.provider.settings.set('secret_key_sandbox', 'sk_test_123')
        self.provider.settings.set('webhook_secret', 'test_webhook_secret')

    def test_settings_form_validation(self):
        """Test that settings form validates required fields"""
        # Test live mode validation
        cleaned_data = {
            'endpoint': 'live',
            'public_key_live': '',
            'secret_key_live': '',
        }
        
        with pytest.raises(ValidationError):
            self.provider.settings_form_clean(cleaned_data)
        
        # Test sandbox mode validation
        cleaned_data = {
            'endpoint': 'sandbox',
            'public_key_sandbox': 'pk_test_123',
            'secret_key_sandbox': 'sk_test_123',
        }
        
        result = self.provider.settings_form_clean(cleaned_data)
        assert result == cleaned_data

    @patch('pretix_paystack.payment.requests.post')
    def test_payment_initialization(self, mock_post):
        """Test payment initialization with Paystack API"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': True,
            'data': {
                'reference': 'test-ref-123',
                'access_code': 'test-access-123',
                'authorization_url': 'https://checkout.paystack.com/test-access-123'
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.provider.payment_perform(Mock(), self.payment)
        
        assert result == 'https://checkout.paystack.com/test-access-123'
        assert self.payment.info_data['paystack_reference'] == 'test-ref-123'
        assert self.payment.info_data['access_code'] == 'test-access-123'

    @patch('pretix_paystack.payment.requests.get')
    def test_payment_verification(self, mock_get):
        """Test payment verification with Paystack API"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': True,
            'data': {
                'id': 123456789,
                'reference': 'test-ref-123',
                'status': 'success',
                'amount': 10000,
                'currency': 'NGN',
                'gateway_response': 'Successful',
                'paid_at': '2023-01-01T12:00:00Z',
                'channel': 'card'
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.provider.verify_payment('test-ref-123')
        
        assert result['status'] is True
        assert result['data']['status'] == 'success'

    def test_webhook_signature_verification(self):
        """Test webhook signature verification"""
        payload = b'{"event": "charge.success", "data": {"reference": "test"}}'
        secret = 'test_webhook_secret'
        
        # Generate correct signature
        correct_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        # Test correct signature
        assert self.provider.verify_webhook_signature(payload, correct_signature) is True
        
        # Test incorrect signature
        assert self.provider.verify_webhook_signature(payload, 'wrong_signature') is False

    def test_webhook_event_processing(self):
        """Test webhook event processing"""
        self.payment.info_data = {'paystack_reference': 'test-ref-123'}
        self.payment.save()
        
        # Test successful payment webhook
        webhook_data = {
            'reference': 'test-ref-123',
            'id': 123456789,
            'status': 'success',
            'gateway_response': 'Successful',
            'paid_at': '2023-01-01T12:00:00Z',
            'channel': 'card',
            'currency': 'NGN',
            'amount': 10000
        }
        
        with patch.object(self.provider, '_find_payment_by_reference', return_value=self.payment):
            result = self.provider.process_webhook_event('charge.success', webhook_data)
            
        assert result is True
        self.payment.refresh_from_db()
        assert self.payment.state == OrderPayment.PAYMENT_STATE_CONFIRMED

    @patch('pretix_paystack.payment.requests.post')
    def test_refund_execution(self, mock_post):
        """Test refund execution"""
        # Set up confirmed payment
        self.payment.state = OrderPayment.PAYMENT_STATE_CONFIRMED
        self.payment.info_data = {'paystack_transaction_id': '123456789'}
        self.payment.save()
        
        # Create refund
        from pretix.base.models import OrderRefund
        refund = OrderRefund.objects.create(
            payment=self.payment,
            source=OrderRefund.REFUND_SOURCE_ADMIN,
            state=OrderRefund.REFUND_STATE_CREATED,
            amount=Decimal('50.00')
        )
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': True,
            'data': {
                'id': 'refund-123',
                'transaction': {'id': '123456789'},
                'status': 'pending'
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        self.provider.execute_refund(refund)
        
        refund.refresh_from_db()
        assert refund.state == OrderRefund.REFUND_STATE_DONE
        assert refund.info_data['paystack_refund_id'] == 'refund-123'

    def test_api_call_error_handling(self):
        """Test API call error handling"""
        with patch('pretix_paystack.payment.requests.post', side_effect=requests.exceptions.RequestException('Network error')):
            with pytest.raises(PaymentException):
                self.provider._make_api_call('POST', '/test', {})


class PaystackWebhookViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.organizer = Organizer.objects.create(name='Test Organizer', slug='test-org')
        self.event = Event.objects.create(
            organizer=self.organizer,
            name='Test Event',
            slug='test-event',
            date_from=now(),
            currency='NGN'
        )
        
        # Configure test settings
        provider = PaystackSettingsHolder(self.event)
        provider.settings.set('webhook_secret', 'test_webhook_secret')

    def test_webhook_missing_signature(self):
        """Test webhook request without signature"""
        from pretix_paystack.views import PaystackWebhookView
        
        request = self.factory.post(
            f'/{self.organizer.slug}/{self.event.slug}/_paystack/webhook/',
            data=json.dumps({'event': 'charge.success'}),
            content_type='application/json'
        )
        
        view = PaystackWebhookView()
        response = view.post(request, event=self.event.slug)
        
        assert response.status_code == 400

    def test_webhook_invalid_signature(self):
        """Test webhook request with invalid signature"""
        from pretix_paystack.views import PaystackWebhookView
        
        payload = json.dumps({'event': 'charge.success', 'data': {'reference': 'test'}})
        request = self.factory.post(
            f'/{self.organizer.slug}/{self.event.slug}/_paystack/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE='invalid_signature'
        )
        
        view = PaystackWebhookView()
        response = view.post(request, event=self.event.slug)
        
        assert response.status_code == 400

    def test_webhook_valid_request(self):
        """Test webhook request with valid signature"""
        from pretix_paystack.views import PaystackWebhookView
        
        payload = json.dumps({'event': 'charge.success', 'data': {'reference': 'test'}})
        signature = hmac.new(
            'test_webhook_secret'.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        request = self.factory.post(
            f'/{self.organizer.slug}/{self.event.slug}/_paystack/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_X_PAYSTACK_SIGNATURE=signature
        )
        
        with patch('pretix_paystack.payment.PaystackSettingsHolder.process_webhook_event', return_value=True):
            view = PaystackWebhookView()
            response = view.post(request, event=self.event.slug)
            
        assert response.status_code == 200


import requests
from django.core.exceptions import ValidationError

def test_empty():
    # put your first tests here
    assert 1 + 1 == 2
