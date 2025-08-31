import os
import pytest
import requests_mock
from decimal import Decimal

from django.test import TestCase
from django.utils.timezone import now

from pretix.base.models import Event, Organizer, Order, OrderPayment
from pretix_paystack.payment import PaystackSettingsHolder


class PaystackIntegrationTest(TestCase):
    """Integration tests that can run against Paystack sandbox or with mocked responses"""
    
    def setUp(self):
        self.organizer = Organizer.objects.create(name='Test Organizer', slug='test-org')
        self.event = Event.objects.create(
            organizer=self.organizer,
            name='Test Event',
            slug='test-event',
            date_from=now(),
            currency='NGN'
        )
        
        # Use environment variables for real API keys if available
        self.test_public_key = os.environ.get('PAYSTACK_TEST_PUBLIC_KEY', 'pk_test_mock')
        self.test_secret_key = os.environ.get('PAYSTACK_TEST_SECRET_KEY', 'sk_test_mock')
        self.webhook_secret = os.environ.get('PAYSTACK_TEST_WEBHOOK_SECRET', 'test_webhook_secret')
        
        self.provider = PaystackSettingsHolder(self.event)
        self.provider.settings.set('endpoint', 'sandbox')
        self.provider.settings.set('public_key_sandbox', self.test_public_key)
        self.provider.settings.set('secret_key_sandbox', self.test_secret_key)
        self.provider.settings.set('webhook_secret', self.webhook_secret)

    @pytest.mark.skipif(
        not all([
            os.environ.get('PAYSTACK_TEST_PUBLIC_KEY'),
            os.environ.get('PAYSTACK_TEST_SECRET_KEY')
        ]),
        reason="Real Paystack API keys not provided"
    )
    def test_real_payment_initialization(self):
        """Test payment initialization with real Paystack sandbox API"""
        order = Order.objects.create(
            code='REAL001',
            event=self.event,
            email='test@example.com',
            status=Order.STATUS_PENDING,
            total=Decimal('100.00')
        )
        payment = OrderPayment.objects.create(
            order=order,
            provider='paystack',
            amount=Decimal('100.00'),
            state=OrderPayment.PAYMENT_STATE_CREATED
        )
        
        # This will make a real API call to Paystack sandbox
        result = self.provider.payment_perform(None, payment)
        
        assert result.startswith('https://checkout.paystack.com/')
        assert 'paystack_reference' in payment.info_data
        assert 'access_code' in payment.info_data

    def test_mocked_payment_flow(self):
        """Test complete payment flow with mocked API responses"""
        order = Order.objects.create(
            code='MOCK001',
            event=self.event,
            email='test@example.com',
            status=Order.STATUS_PENDING,
            total=Decimal('100.00')
        )
        payment = OrderPayment.objects.create(
            order=order,
            provider='paystack',
            amount=Decimal('100.00'),
            state=OrderPayment.PAYMENT_STATE_CREATED
        )
        
        with requests_mock.Mocker() as m:
            # Mock payment initialization
            m.post('https://api.paystack.co/transaction/initialize', json={
                'status': True,
                'data': {
                    'reference': 'mock-ref-123',
                    'access_code': 'mock-access-123',
                    'authorization_url': 'https://checkout.paystack.com/mock-access-123'
                }
            })
            
            # Mock payment verification
            m.get('https://api.paystack.co/transaction/verify/mock-ref-123', json={
                'status': True,
                'data': {
                    'id': 123456789,
                    'reference': 'mock-ref-123',
                    'status': 'success',
                    'amount': 10000,
                    'currency': 'NGN',
                    'gateway_response': 'Successful',
                    'paid_at': '2023-01-01T12:00:00Z',
                    'channel': 'card'
                }
            })
            
            # Test payment initialization
            result = self.provider.payment_perform(None, payment)
            assert result == 'https://checkout.paystack.com/mock-access-123'
            
            # Test payment verification
            verification_result = self.provider.verify_payment('mock-ref-123')
            assert verification_result['data']['status'] == 'success'

    def test_mocked_refund_flow(self):
        """Test refund flow with mocked API responses"""
        order = Order.objects.create(
            code='REFUND001',
            event=self.event,
            email='test@example.com',
            status=Order.STATUS_PENDING,
            total=Decimal('100.00')
        )
        payment = OrderPayment.objects.create(
            order=order,
            provider='paystack',
            amount=Decimal('100.00'),
            state=OrderPayment.PAYMENT_STATE_CONFIRMED,
            info={'paystack_transaction_id': '123456789'}
        )
        
        from pretix.base.models import OrderRefund
        refund = OrderRefund.objects.create(
            payment=payment,
            source=OrderRefund.REFUND_SOURCE_ADMIN,
            state=OrderRefund.REFUND_STATE_CREATED,
            amount=Decimal('50.00')
        )
        
        with requests_mock.Mocker() as m:
            # Mock refund request
            m.post('https://api.paystack.co/refund', json={
                'status': True,
                'data': {
                    'id': 'refund-123',
                    'transaction': {'id': '123456789'},
                    'status': 'pending',
                    'amount': 5000,
                    'currency': 'NGN'
                }
            })
            
            # Test refund execution
            self.provider.execute_refund(refund)
            
            refund.refresh_from_db()
            assert refund.state == OrderRefund.REFUND_STATE_DONE
            assert refund.info_data['paystack_refund_id'] == 'refund-123'

    def test_webhook_end_to_end(self):
        """Test complete webhook processing flow"""
        order = Order.objects.create(
            code='WEBHOOK001',
            event=self.event,
            email='test@example.com',
            status=Order.STATUS_PENDING,
            total=Decimal('100.00')
        )
        payment = OrderPayment.objects.create(
            order=order,
            provider='paystack',
            amount=Decimal('100.00'),
            state=OrderPayment.PAYMENT_STATE_CREATED,
            info={'paystack_reference': 'webhook-ref-123'}
        )
        
        # Simulate webhook data
        webhook_data = {
            'reference': 'webhook-ref-123',
            'id': 123456789,
            'status': 'success',
            'gateway_response': 'Successful',
            'paid_at': '2023-01-01T12:00:00Z',
            'channel': 'card',
            'currency': 'NGN',
            'amount': 10000
        }
        
        # Process webhook event
        result = self.provider.process_webhook_event('charge.success', webhook_data)
        
        assert result is True
        payment.refresh_from_db()
        assert payment.state == OrderPayment.PAYMENT_STATE_CONFIRMED
        assert payment.info_data['paystack_transaction_id'] == 123456789

    def test_reconciliation_flow(self):
        """Test payment reconciliation flow"""
        from pretix_paystack.tasks import _reconcile_single_payment
        
        order = Order.objects.create(
            code='RECONCILE001',
            event=self.event,
            email='test@example.com',
            status=Order.STATUS_PENDING,
            total=Decimal('100.00')
        )
        payment = OrderPayment.objects.create(
            order=order,
            provider='paystack',
            amount=Decimal('100.00'),
            state=OrderPayment.PAYMENT_STATE_CREATED,
            info={'paystack_reference': 'reconcile-ref-123'}
        )
        
        with requests_mock.Mocker() as m:
            # Mock verification API call
            m.get('https://api.paystack.co/transaction/verify/reconcile-ref-123', json={
                'status': True,
                'data': {
                    'id': 123456789,
                    'reference': 'reconcile-ref-123',
                    'status': 'success',
                    'amount': 10000,
                    'currency': 'NGN',
                    'gateway_response': 'Successful',
                    'paid_at': '2023-01-01T12:00:00Z',
                    'channel': 'card'
                }
            })
            
            # Test reconciliation
            result = _reconcile_single_payment(self.provider, payment)
            
            assert result == 'confirmed'
            payment.refresh_from_db()
            assert payment.state == OrderPayment.PAYMENT_STATE_CONFIRMED
            assert 'reconciled_at' in payment.info_data
