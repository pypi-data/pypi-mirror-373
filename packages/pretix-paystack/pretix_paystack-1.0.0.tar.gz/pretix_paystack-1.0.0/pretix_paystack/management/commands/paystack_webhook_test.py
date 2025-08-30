import hashlib
import hmac
import json
import requests
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from pretix.base.models import Event
from pretix_paystack.payment import PaystackSettingsHolder


class Command(BaseCommand):
    help = 'Test Paystack webhook integration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--event',
            type=str,
            required=True,
            help='Event slug to test (format: organizer/event)',
        )
        parser.add_argument(
            '--webhook-url',
            type=str,
            help='Override webhook URL (default: auto-detect)',
        )
        parser.add_argument(
            '--test-event',
            type=str,
            default='charge.success',
            choices=['charge.success', 'charge.failed', 'charge.dispute.create'],
            help='Type of webhook event to simulate',
        )
        parser.add_argument(
            '--reference',
            type=str,
            help='Payment reference to use in test (required for realistic testing)',
        )

    def handle(self, *args, **options):
        try:
            organizer_slug, event_slug = options['event'].split('/')
            event = Event.objects.get(slug=event_slug, organizer__slug=organizer_slug)
        except (ValueError, Event.DoesNotExist):
            raise CommandError(f'Event not found: {options["event"]}')
        
        provider = PaystackSettingsHolder(event)
        webhook_secret = provider.settings.get('webhook_secret')
        
        if not webhook_secret:
            raise CommandError('Webhook secret not configured for this event')
        
        # Generate test webhook payload
        test_data = self._generate_test_payload(
            options['test_event'], 
            options.get('reference', f'test-{datetime.now().strftime("%Y%m%d%H%M%S")}')
        )
        
        # Generate signature
        payload_json = json.dumps(test_data)
        signature = self._generate_signature(payload_json.encode(), webhook_secret)
        
        # Determine webhook URL
        if options['webhook_url']:
            webhook_url = options['webhook_url']
        else:
            # Auto-detect webhook URL (this would need to be adjusted for your setup)
            webhook_url = f'http://localhost:8000/{organizer_slug}/{event_slug}/_paystack/webhook/'
        
        self.stdout.write(f'Testing webhook: {webhook_url}')
        self.stdout.write(f'Event type: {options["test_event"]}')
        self.stdout.write(f'Reference: {test_data["data"]["reference"]}')
        self.stdout.write('')
        
        # Send test webhook
        headers = {
            'X-Paystack-Signature': signature,
            'Content-Type': 'application/json',
        }
        
        try:
            response = requests.post(webhook_url, json=test_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✓ Webhook test successful'))
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Webhook test failed: {response.status_code} {response.text}')
                )
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to send webhook: {str(e)}'))
        
        # Show curl command for manual testing
        self.stdout.write('')
        self.stdout.write('Manual test command:')
        self.stdout.write(f'curl -X POST {webhook_url} \\')
        self.stdout.write(f'  -H "X-Paystack-Signature: {signature}" \\')
        self.stdout.write('  -H "Content-Type: application/json" \\')
        self.stdout.write(f"  -d '{payload_json}'")

    def _generate_test_payload(self, event_type, reference):
        """Generate test webhook payload"""
        # Randomize channel for testing different payment methods
        import random
        channels = ['card', 'mobile_money', 'bank', 'ussd', 'qr']
        test_channel = random.choice(channels)
        
        base_data = {
            'id': 123456789,
            'reference': reference,
            'amount': 50000,  # 500.00 in kobo
            'currency': 'NGN',
            'channel': test_channel,
            'status': 'success' if 'success' in event_type else 'failed',
            'paid_at': datetime.now().isoformat(),
            'gateway_response': 'Successful' if 'success' in event_type else 'Declined',
            'customer': {
                'email': 'test@example.com',
                'customer_code': 'CUS_test123'
            }
        }
        
        # Add channel-specific data
        if test_channel == 'card':
            base_data['authorization'] = {
                'authorization_code': 'AUTH_test123',
                'bin': '408408',
                'last4': '4081',
                'exp_month': '12',
                'exp_year': '2025',
                'channel': 'card',
                'card_type': 'visa DEBIT',
                'bank': 'Test Bank',
                'country_code': 'NG',
                'brand': 'visa',
                'reusable': True,
                'signature': 'SIG_test123'
            }
        elif test_channel == 'mobile_money':
            base_data['mobile_money'] = {
                'phone': '254708374149',
                'provider': 'mpesa',
                'transaction_id': 'MPESA123456789'
            }
        elif test_channel == 'bank':
            base_data['bank'] = {
                'account_number': '0123456789',
                'bank_name': 'Test Bank',
                'bank_code': '044'
            }
        elif test_channel == 'ussd':
            base_data['ussd'] = {
                'ussd_code': '*737*000*amount#',
                'provider': 'gtbank'
            }
        
        if event_type == 'charge.dispute.create':
            base_data.update({
                'status': 'success',  # Original transaction was successful
                'dispute': {
                    'id': 987654321,
                    'refund_amount': 50000,
                    'currency': 'NGN',
                    'status': 'pending',
                    'resolution': None,
                    'domain': 'test',
                    'due_at': datetime.now().isoformat(),
                    'reason': 'duplicate',
                    'history': []
                }
            })
        
        return {
            'event': event_type,
            'data': base_data
        }

    def _generate_signature(self, payload, secret):
        """Generate Paystack webhook signature"""
        return hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
