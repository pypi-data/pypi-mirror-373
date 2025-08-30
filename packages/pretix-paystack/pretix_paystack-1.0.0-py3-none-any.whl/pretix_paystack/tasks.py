import logging
from datetime import datetime, timedelta
from typing import List

from celery import shared_task
from django.utils.timezone import now

from pretix.base.models import Event, OrderPayment
from pretix.base.services.tasks import ProfiledTask

from .payment import PaystackSettingsHolder

logger = logging.getLogger(__name__)


@shared_task(base=ProfiledTask, bind=True)
def reconcile_pending_payments(self, event_id: int = None, payment_ids: List[int] = None):
    """
    Reconcile pending Paystack payments by verifying their status with Paystack API.
    
    Args:
        event_id: If provided, reconcile all pending payments for this event
        payment_ids: If provided, reconcile only these specific payments
    """
    try:
        if event_id:
            event = Event.objects.get(pk=event_id)
            provider = PaystackSettingsHolder(event)
            
            # Check if reconciliation is enabled
            if not provider.settings.get('reconciliation_enabled', True):
                logger.info(f'Reconciliation disabled for event {event.slug}')
                return {'status': 'disabled', 'event': event.slug}
            
            # Get threshold from settings (default 10 minutes)
            threshold_minutes = provider.settings.get('reconciliation_threshold', 10)
            threshold_time = now() - timedelta(minutes=threshold_minutes)
            
            # Find pending payments older than threshold
            pending_payments = OrderPayment.objects.filter(
                order__event=event,
                provider='paystack',
                state__in=[OrderPayment.PAYMENT_STATE_CREATED, OrderPayment.PAYMENT_STATE_PENDING],
                created__lt=threshold_time
            ).select_related('order')
            
        elif payment_ids:
            # Reconcile specific payments
            pending_payments = OrderPayment.objects.filter(
                pk__in=payment_ids,
                provider='paystack',
                state__in=[OrderPayment.PAYMENT_STATE_CREATED, OrderPayment.PAYMENT_STATE_PENDING]
            ).select_related('order')
            
            if not pending_payments.exists():
                logger.warning(f'No pending payments found for IDs: {payment_ids}')
                return {'status': 'no_payments', 'payment_ids': payment_ids}
                
            # Get event and provider from first payment
            event = pending_payments.first().order.event
            provider = PaystackSettingsHolder(event)
            
        else:
            logger.error('Either event_id or payment_ids must be provided')
            return {'status': 'error', 'message': 'Missing parameters'}
        
        reconciled_count = 0
        confirmed_count = 0
        failed_count = 0
        error_count = 0
        
        logger.info(f'Starting reconciliation for {pending_payments.count()} payments')
        
        for payment in pending_payments:
            try:
                result = _reconcile_single_payment(provider, payment)
                reconciled_count += 1
                
                if result == 'confirmed':
                    confirmed_count += 1
                elif result == 'failed':
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f'Failed to reconcile payment {payment.pk}: {str(e)}')
                error_count += 1
        
        result = {
            'status': 'completed',
            'event': event.slug,
            'total_payments': pending_payments.count(),
            'reconciled': reconciled_count,
            'confirmed': confirmed_count,
            'failed': failed_count,
            'errors': error_count,
        }
        
        logger.info(f'Reconciliation completed: {result}')
        return result
        
    except Event.DoesNotExist:
        logger.error(f'Event not found: {event_id}')
        return {'status': 'error', 'message': 'Event not found'}
    except Exception as e:
        logger.error(f'Reconciliation task failed: {str(e)}')
        return {'status': 'error', 'message': str(e)}


def _reconcile_single_payment(provider: PaystackSettingsHolder, payment: OrderPayment) -> str:
    """
    Reconcile a single payment with Paystack API.
    
    Returns:
        'confirmed': Payment was confirmed
        'failed': Payment was marked as failed
        'unchanged': Payment status unchanged
    """
    reference = payment.info_data.get('paystack_reference')
    if not reference:
        logger.warning(f'Payment {payment.pk} missing Paystack reference')
        return 'unchanged'
    
    try:
        # Verify payment status with Paystack
        verification_response = provider.verify_payment(reference)
        
        if not verification_response.get('status'):
            logger.warning(f'Payment verification failed for {payment.pk}: {verification_response}')
            return 'unchanged'
        
        paystack_data = verification_response.get('data', {})
        paystack_status = paystack_data.get('status')
        
        # Update payment info with latest data
        payment.info_data.update({
            'paystack_transaction_id': paystack_data.get('id'),
            'paystack_status': paystack_status,
            'paystack_gateway_response': paystack_data.get('gateway_response'),
            'paystack_paid_at': paystack_data.get('paid_at'),
            'paystack_channel': paystack_data.get('channel'),
            'paystack_currency': paystack_data.get('currency'),
            'paystack_amount': paystack_data.get('amount'),
            'reconciled_at': now().isoformat(),
        })
        
        if paystack_status == 'success':
            # Payment successful - confirm if not already confirmed
            if payment.state == OrderPayment.PAYMENT_STATE_CREATED:
                payment.confirm()
                logger.info(f'Payment {payment.pk} confirmed via reconciliation')
                return 'confirmed'
            else:
                logger.info(f'Payment {payment.pk} already confirmed')
                payment.save(update_fields=['info'])
                return 'unchanged'
                
        elif paystack_status in ['failed', 'cancelled', 'abandoned']:
            # Payment failed - mark as failed if not already processed
            if payment.state == OrderPayment.PAYMENT_STATE_CREATED:
                payment.fail(info=paystack_data.get('gateway_response', f'Payment {paystack_status}'))
                logger.info(f'Payment {payment.pk} marked as failed via reconciliation: {paystack_status}')
                return 'failed'
            else:
                logger.info(f'Payment {payment.pk} already processed')
                payment.save(update_fields=['info'])
                return 'unchanged'
                
        else:
            # Payment still pending or unknown status
            logger.info(f'Payment {payment.pk} still pending: {paystack_status}')
            payment.save(update_fields=['info'])
            return 'unchanged'
            
    except Exception as e:
        logger.error(f'Error reconciling payment {payment.pk}: {str(e)}')
        raise


@shared_task(base=ProfiledTask, bind=True)
def periodic_reconciliation(self):
    """
    Periodic task to reconcile pending payments across all events.
    This should be scheduled to run every few minutes via Celery beat.
    """
    try:
        # Find all events with Paystack enabled and reconciliation enabled
        events_with_paystack = Event.objects.filter(
            settings__payment_paystack__enabled='True',
            settings__payment_paystack__reconciliation_enabled='True'
        )
        
        total_events = 0
        total_reconciled = 0
        
        for event in events_with_paystack:
            try:
                provider = PaystackSettingsHolder(event)
                
                # Get reconciliation interval (default 10 minutes)
                interval_minutes = provider.settings.get('reconciliation_interval', 10)
                
                # Check if enough time has passed since last reconciliation
                last_run_key = f'paystack_last_reconciliation_{event.pk}'
                last_run = provider.settings.get(last_run_key)
                
                if last_run:
                    last_run_time = datetime.fromisoformat(last_run)
                    if now() - last_run_time < timedelta(minutes=interval_minutes):
                        continue  # Skip this event, not enough time passed
                
                # Run reconciliation for this event
                result = reconcile_pending_payments.delay(event_id=event.pk)
                
                # Update last run timestamp
                provider.settings.set(last_run_key, now().isoformat())
                
                total_events += 1
                logger.info(f'Scheduled reconciliation for event {event.slug}')
                
            except Exception as e:
                logger.error(f'Failed to schedule reconciliation for event {event.slug}: {str(e)}')
        
        result = {
            'status': 'completed',
            'events_processed': total_events,
            'timestamp': now().isoformat(),
        }
        
        logger.info(f'Periodic reconciliation completed: {result}')
        return result
        
    except Exception as e:
        logger.error(f'Periodic reconciliation task failed: {str(e)}')
        return {'status': 'error', 'message': str(e)}


@shared_task(base=ProfiledTask, bind=True)
def cleanup_old_payment_data(self, days_old: int = 90):
    """
    Clean up old payment reconciliation data to prevent database bloat.
    
    Args:
        days_old: Remove reconciliation data older than this many days
    """
    try:
        cutoff_date = now() - timedelta(days=days_old)
        
        # Find payments with old reconciliation data
        payments_to_clean = OrderPayment.objects.filter(
            provider='paystack',
            created__lt=cutoff_date,
            info__contains='reconciled_at'
        )
        
        cleaned_count = 0
        
        for payment in payments_to_clean:
            # Remove reconciliation metadata but keep essential Paystack data
            essential_keys = [
                'paystack_reference',
                'paystack_transaction_id',
                'paystack_status',
                'access_code',
                'authorization_url'
            ]
            
            cleaned_info = {k: v for k, v in payment.info_data.items() if k in essential_keys}
            
            if cleaned_info != payment.info_data:
                payment.info_data = cleaned_info
                payment.save(update_fields=['info'])
                cleaned_count += 1
        
        result = {
            'status': 'completed',
            'payments_cleaned': cleaned_count,
            'cutoff_date': cutoff_date.isoformat(),
        }
        
        logger.info(f'Payment data cleanup completed: {result}')
        return result
        
    except Exception as e:
        logger.error(f'Payment data cleanup failed: {str(e)}')
        return {'status': 'error', 'message': str(e)}
