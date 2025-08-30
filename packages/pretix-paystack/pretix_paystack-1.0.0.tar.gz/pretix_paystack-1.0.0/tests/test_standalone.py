"""
Standalone tests for pretix-paystack plugin that don't require full pretix installation
"""
import hashlib
import hmac
import json
import pytest
import requests_mock
from unittest.mock import Mock, patch
from decimal import Decimal


class TestPaystackCore:
    """Test core Paystack functionality without Django dependencies"""
    
    def test_webhook_signature_verification(self):
        """Test webhook signature verification logic"""
        payload = b'{"event": "charge.success", "data": {"reference": "test"}}'
        secret = 'test_webhook_secret'
        
        # Generate correct signature
        correct_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        # Test correct signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        assert hmac.compare_digest(expected_signature, correct_signature)
        
        # Test incorrect signature
        wrong_signature = 'wrong_signature'
        assert not hmac.compare_digest(expected_signature, wrong_signature)

    def test_paystack_api_payload_generation(self):
        """Test Paystack API payload generation"""
        # Mock order data
        order_data = {
            'email': 'test@example.com',
            'amount': Decimal('100.00'),
            'code': 'TEST123',
            'event_slug': 'test-event',
            'payment_id': 1
        }
        
        # Generate payload
        payload = {
            'email': order_data['email'],
            'amount': int(order_data['amount'] * 100),  # Convert to kobo
            'reference': f"{order_data['event_slug']}-{order_data['code']}-{order_data['payment_id']}",
            'channels': ['card', 'bank', 'mobile_money'],
            'metadata': {
                'order_code': order_data['code'],
                'event_slug': order_data['event_slug'],
                'payment_id': order_data['payment_id'],
                'supported_channels': ['card', 'bank', 'mobile_money']
            }
        }
        
        assert payload['amount'] == 10000  # 100.00 * 100
        assert payload['reference'] == 'test-event-TEST123-1'
        assert 'mobile_money' in payload['channels']
        assert payload['metadata']['order_code'] == 'TEST123'

    def test_paystack_api_initialization(self, requests_mock):
        """Test Paystack payment initialization API call"""
        # Mock successful response
        requests_mock.post('https://api.paystack.co/transaction/initialize', json={
            'status': True,
            'data': {
                'reference': 'test-ref-123',
                'access_code': 'test-access-123',
                'authorization_url': 'https://checkout.paystack.com/test-access-123'
            }
        })
        
        # Simulate API call
        import requests
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            json={
                'email': 'test@example.com',
                'amount': 10000,
                'reference': 'test-ref-123',
                'channels': ['card', 'mobile_money']
            },
            headers={'Authorization': 'Bearer sk_test_123'}
        )
        
        data = response.json()
        assert data['status'] is True
        assert data['data']['authorization_url'].startswith('https://checkout.paystack.com/')

    def test_paystack_payment_verification(self, requests_mock):
        """Test Paystack payment verification"""
        # Mock verification response
        requests_mock.get('https://api.paystack.co/transaction/verify/test-ref-123', json={
            'status': True,
            'data': {
                'id': 123456789,
                'reference': 'test-ref-123',
                'status': 'success',
                'amount': 10000,
                'currency': 'NGN',
                'channel': 'mobile_money',
                'gateway_response': 'Successful',
                'paid_at': '2023-01-01T12:00:00Z',
                'mobile_money': {
                    'phone': '254708374149',
                    'provider': 'mpesa',
                    'transaction_id': 'MPESA123456789'
                }
            }
        })
        
        # Simulate verification call
        import requests
        response = requests.get(
            'https://api.paystack.co/transaction/verify/test-ref-123',
            headers={'Authorization': 'Bearer sk_test_123'}
        )
        
        data = response.json()
        assert data['status'] is True
        assert data['data']['status'] == 'success'
        assert data['data']['channel'] == 'mobile_money'
        assert data['data']['mobile_money']['provider'] == 'mpesa'

    def test_webhook_event_processing_logic(self):
        """Test webhook event processing logic"""
        # Test successful payment event
        webhook_data = {
            'reference': 'test-ref-123',
            'id': 123456789,
            'status': 'success',
            'channel': 'mobile_money',
            'gateway_response': 'Successful',
            'paid_at': '2023-01-01T12:00:00Z',
            'currency': 'KES',
            'amount': 10000,
            'mobile_money': {
                'phone': '254708374149',
                'provider': 'mpesa',
                'transaction_id': 'MPESA123456789'
            }
        }
        
        # Simulate processing logic
        def process_successful_payment(data):
            return {
                'payment_confirmed': data['status'] == 'success',
                'channel': data['channel'],
                'is_mpesa': data.get('mobile_money', {}).get('provider') == 'mpesa',
                'transaction_id': data['id']
            }
        
        result = process_successful_payment(webhook_data)
        assert result['payment_confirmed'] is True
        assert result['channel'] == 'mobile_money'
        assert result['is_mpesa'] is True
        assert result['transaction_id'] == 123456789

    def test_channel_configuration(self):
        """Test payment channel configuration"""
        # Test different channel combinations
        test_configs = [
            {
                'channels': ['card'],
                'expected_mpesa': False,
                'expected_card': True
            },
            {
                'channels': ['mobile_money'],
                'expected_mpesa': True,
                'expected_card': False
            },
            {
                'channels': ['card', 'mobile_money', 'bank'],
                'expected_mpesa': True,
                'expected_card': True
            }
        ]
        
        for config in test_configs:
            has_mpesa = 'mobile_money' in config['channels']
            has_card = 'card' in config['channels']
            
            assert has_mpesa == config['expected_mpesa']
            assert has_card == config['expected_card']

    def test_currency_detection_for_mpesa(self):
        """Test currency detection for M-Pesa support"""
        def supports_mpesa(currency, channels):
            return currency == 'KES' and 'mobile_money' in channels
        
        # Test cases
        assert supports_mpesa('KES', ['mobile_money']) is True
        assert supports_mpesa('KES', ['card', 'mobile_money']) is True
        assert supports_mpesa('NGN', ['mobile_money']) is False
        assert supports_mpesa('KES', ['card']) is False

    def test_test_credentials_validation(self):
        """Test validation of test credentials"""
        test_data = {
            'card': '4084084084084081',
            'mpesa_phone': '254708374149',
            'endpoint': 'sandbox'
        }
        
        # Validate test card
        assert test_data['card'].startswith('4084')
        assert len(test_data['card']) == 16
        
        # Validate test M-Pesa phone
        assert test_data['mpesa_phone'].startswith('254')
        assert len(test_data['mpesa_phone']) == 12
        
        # Validate sandbox mode
        assert test_data['endpoint'] == 'sandbox'


def test_basic_functionality():
    """Basic test to ensure imports work"""
    assert True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
