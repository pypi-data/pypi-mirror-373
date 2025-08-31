from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now

from pretix.base.models import Event, OrderPayment
from pretix_paystack.payment import PaystackSettingsHolder
from pretix_paystack.tasks import reconcile_pending_payments


class Command(BaseCommand):
    help = 'Reconcile pending Paystack payments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--event',
            type=str,
            help='Event slug to reconcile (format: organizer/event)',
        )
        parser.add_argument(
            '--payment-id',
            type=int,
            action='append',
            help='Specific payment ID to reconcile (can be used multiple times)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be reconciled without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reconciliation even if disabled in settings',
        )

    def handle(self, *args, **options):
        if options['event']:
            try:
                organizer_slug, event_slug = options['event'].split('/')
                event = Event.objects.get(slug=event_slug, organizer__slug=organizer_slug)
            except (ValueError, Event.DoesNotExist):
                raise CommandError(f'Event not found: {options["event"]}')
            
            provider = PaystackSettingsHolder(event)
            
            if not options['force'] and not provider.settings.get('reconciliation_enabled', True):
                self.stdout.write(
                    self.style.WARNING(f'Reconciliation disabled for event {event.slug}')
                )
                return
            
            if options['dry_run']:
                self._dry_run_event(event, provider)
            else:
                result = reconcile_pending_payments(event_id=event.pk)
                self._print_result(result)
                
        elif options['payment_id']:
            if options['dry_run']:
                self._dry_run_payments(options['payment_id'])
            else:
                result = reconcile_pending_payments(payment_ids=options['payment_id'])
                self._print_result(result)
                
        else:
            # Reconcile all events
            if options['dry_run']:
                self._dry_run_all()
            else:
                from pretix_paystack.tasks import periodic_reconciliation
                result = periodic_reconciliation()
                self._print_result(result)

    def _dry_run_event(self, event, provider):
        """Show what would be reconciled for an event"""
        threshold_minutes = provider.settings.get('reconciliation_threshold', 10)
        threshold_time = now() - timedelta(minutes=threshold_minutes)
        
        pending_payments = OrderPayment.objects.filter(
            order__event=event,
            provider='paystack',
            state__in=[OrderPayment.PAYMENT_STATE_CREATED, OrderPayment.PAYMENT_STATE_PENDING],
            created__lt=threshold_time
        ).select_related('order')
        
        self.stdout.write(f'Event: {event.slug}')
        self.stdout.write(f'Pending payments to reconcile: {pending_payments.count()}')
        
        for payment in pending_payments:
            reference = payment.info_data.get('paystack_reference', 'No reference')
            self.stdout.write(
                f'  - Payment {payment.pk} (Order: {payment.order.code}, '
                f'Reference: {reference}, Created: {payment.created})'
            )

    def _dry_run_payments(self, payment_ids):
        """Show what would be reconciled for specific payments"""
        payments = OrderPayment.objects.filter(
            pk__in=payment_ids,
            provider='paystack'
        ).select_related('order')
        
        self.stdout.write(f'Payments to reconcile: {payments.count()}')
        
        for payment in payments:
            reference = payment.info_data.get('paystack_reference', 'No reference')
            self.stdout.write(
                f'  - Payment {payment.pk} (Order: {payment.order.code}, '
                f'Reference: {reference}, State: {payment.state})'
            )

    def _dry_run_all(self):
        """Show what would be reconciled across all events"""
        events_with_paystack = Event.objects.filter(
            settings__payment_paystack__enabled='True',
            settings__payment_paystack__reconciliation_enabled='True'
        )
        
        self.stdout.write(f'Events with Paystack reconciliation enabled: {events_with_paystack.count()}')
        
        for event in events_with_paystack:
            provider = PaystackSettingsHolder(event)
            self._dry_run_event(event, provider)
            self.stdout.write('')

    def _print_result(self, result):
        """Print reconciliation result"""
        if result.get('status') == 'completed':
            self.stdout.write(
                self.style.SUCCESS(
                    f'Reconciliation completed: {result.get("reconciled", 0)} payments processed, '
                    f'{result.get("confirmed", 0)} confirmed, {result.get("failed", 0)} failed'
                )
            )
        elif result.get('status') == 'error':
            self.stdout.write(
                self.style.ERROR(f'Reconciliation failed: {result.get("message", "Unknown error")}')
            )
        else:
            self.stdout.write(f'Result: {result}')
