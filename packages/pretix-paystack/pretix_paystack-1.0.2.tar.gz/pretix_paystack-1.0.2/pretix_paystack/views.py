import json
import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from pretix.base.models import Event, Order, OrderPayment
from pretix.control.permissions import EventPermissionRequiredMixin
from pretix.multidomain.urlreverse import eventreverse

from .payment import PaystackSettingsHolder

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(View):
    """Handle Paystack webhook notifications"""
    
    def post(self, request, *args, **kwargs):
        try:
            # Get event from URL
            event = get_object_or_404(Event, slug=kwargs.get('event'))
            
            # Initialize payment provider
            provider = PaystackSettingsHolder(event)
            
            # Get webhook payload and signature
            payload = request.body
            signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
            
            if not signature:
                logger.warning('Webhook received without signature')
                return HttpResponseBadRequest('Missing signature')
            
            # Verify webhook signature
            if not provider.verify_webhook_signature(payload, signature):
                logger.warning('Webhook signature verification failed')
                return HttpResponseBadRequest('Invalid signature')
            
            # Parse webhook data
            try:
                webhook_data = json.loads(payload.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f'Invalid webhook payload: {str(e)}')
                return HttpResponseBadRequest('Invalid payload')
            
            event_type = webhook_data.get('event')
            data = webhook_data.get('data', {})
            
            if not event_type:
                logger.error('Webhook missing event type')
                return HttpResponseBadRequest('Missing event type')
            
            # Process webhook event
            success = provider.process_webhook_event(event_type, data)
            
            if success:
                logger.info(f'Webhook processed successfully: {event_type}')
                return HttpResponse('OK')
            else:
                logger.error(f'Webhook processing failed: {event_type}')
                return HttpResponseBadRequest('Processing failed')
                
        except Event.DoesNotExist:
            logger.error('Webhook for non-existent event')
            return HttpResponseBadRequest('Event not found')
        except Exception as e:
            logger.error(f'Webhook processing error: {str(e)}')
            return HttpResponseBadRequest('Internal error')


class PaystackReturnView(View):
    """Handle return from Paystack payment page"""
    
    def get(self, request, *args, **kwargs):
        try:
            # Get parameters from URL
            order_code = kwargs.get('order')
            order_secret = kwargs.get('secret')
            payment_id = kwargs.get('payment')
            
            # Get event from URL
            event = get_object_or_404(Event, slug=kwargs.get('event'))
            
            # Get order and payment
            order = get_object_or_404(Order, code=order_code, event=event, secret=order_secret)
            payment = get_object_or_404(OrderPayment, pk=payment_id, order=order)
            
            # Initialize payment provider
            provider = PaystackSettingsHolder(event)
            
            # Get Paystack reference from payment info
            reference = payment.info_data.get('paystack_reference')
            if not reference:
                logger.error(f'Payment {payment.pk} missing Paystack reference')
                messages.error(request, 'Payment verification failed')
                return redirect(eventreverse(event, 'presale:event.order.pay', kwargs={
                    'order': order.code,
                    'secret': order.secret,
                }))
            
            # Verify payment with Paystack
            try:
                verification_response = provider.verify_payment(reference)
                
                if (verification_response.get('status') and 
                    verification_response.get('data', {}).get('status') == 'success'):
                    
                    # Payment successful - update payment info and confirm
                    payment.info_data.update({
                        'paystack_transaction_id': verification_response['data']['id'],
                        'paystack_status': verification_response['data']['status'],
                        'paystack_gateway_response': verification_response['data']['gateway_response'],
                        'paystack_paid_at': verification_response['data']['paid_at'],
                        'paystack_channel': verification_response['data']['channel'],
                        'paystack_currency': verification_response['data']['currency'],
                        'paystack_amount': verification_response['data']['amount'],
                    })
                    
                    if payment.state == OrderPayment.PAYMENT_STATE_CREATED:
                        payment.confirm()
                        logger.info(f'Payment {payment.pk} confirmed via return URL')
                    
                    messages.success(request, 'Payment successful!')
                    return redirect(eventreverse(event, 'presale:event.order.detail', kwargs={
                        'order': order.code,
                        'secret': order.secret,
                    }))
                    
                else:
                    # Payment failed
                    payment.info_data.update({
                        'paystack_status': verification_response.get('data', {}).get('status', 'failed'),
                        'paystack_gateway_response': verification_response.get('data', {}).get('gateway_response', 'Payment failed'),
                    })
                    
                    if payment.state == OrderPayment.PAYMENT_STATE_CREATED:
                        payment.fail(info='Payment verification failed')
                        logger.info(f'Payment {payment.pk} marked as failed via return URL')
                    
                    messages.error(request, 'Payment was not successful. Please try again.')
                    return redirect(eventreverse(event, 'presale:event.order.pay', kwargs={
                        'order': order.code,
                        'secret': order.secret,
                    }))
                    
            except Exception as e:
                logger.error(f'Payment verification failed for {payment.pk}: {str(e)}')
                messages.error(request, 'Payment verification failed. Please contact support.')
                return redirect(eventreverse(event, 'presale:event.order.pay', kwargs={
                    'order': order.code,
                    'secret': order.secret,
                }))
                
        except (Order.DoesNotExist, OrderPayment.DoesNotExist, Event.DoesNotExist):
            raise Http404('Order or payment not found')
        except Exception as e:
            logger.error(f'Return URL processing error: {str(e)}')
            messages.error(request, 'An error occurred. Please contact support.')
            return redirect('/')


class PaystackReconcileView(EventPermissionRequiredMixin, TemplateView):
    """Manual reconciliation view for admin"""
    template_name = 'pretix_paystack/reconcile.html'
    permission = 'can_change_event_settings'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get pending payments for this event
        pending_payments = OrderPayment.objects.filter(
            order__event=self.request.event,
            provider='paystack',
            state__in=[OrderPayment.PAYMENT_STATE_CREATED, OrderPayment.PAYMENT_STATE_PENDING]
        ).select_related('order').order_by('-created')
        
        context.update({
            'pending_payments': pending_payments,
            'event': self.request.event,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Manual reconciliation trigger"""
        if 'reconcile_all' in request.POST:
            # Trigger reconciliation for all pending payments
            from .tasks import reconcile_pending_payments
            reconcile_pending_payments.delay(self.request.event.pk)
            messages.success(request, 'Reconciliation job started. Check back in a few minutes.')
        
        elif 'reconcile_payment' in request.POST:
            # Reconcile specific payment
            payment_id = request.POST.get('payment_id')
            try:
                payment = OrderPayment.objects.get(
                    pk=payment_id,
                    order__event=self.request.event,
                    provider='paystack'
                )
                
                provider = PaystackSettingsHolder(self.request.event)
                reference = payment.info_data.get('paystack_reference')
                
                if reference:
                    verification_response = provider.verify_payment(reference)
                    
                    if (verification_response.get('status') and 
                        verification_response.get('data', {}).get('status') == 'success'):
                        
                        payment.info_data.update({
                            'paystack_transaction_id': verification_response['data']['id'],
                            'paystack_status': verification_response['data']['status'],
                            'paystack_gateway_response': verification_response['data']['gateway_response'],
                        })
                        
                        if payment.state == OrderPayment.PAYMENT_STATE_CREATED:
                            payment.confirm()
                            messages.success(request, f'Payment {payment.pk} confirmed successfully.')
                        else:
                            messages.info(request, f'Payment {payment.pk} was already processed.')
                    else:
                        messages.warning(request, f'Payment {payment.pk} verification failed or payment not successful.')
                else:
                    messages.error(request, f'Payment {payment.pk} missing Paystack reference.')
                    
            except OrderPayment.DoesNotExist:
                messages.error(request, 'Payment not found.')
            except Exception as e:
                logger.error(f'Manual reconciliation failed: {str(e)}')
                messages.error(request, 'Reconciliation failed. Please try again.')
        
        return redirect(request.get_full_path())


@require_http_methods(["GET"])
def webhook_info_view(request, organizer, event):
    """Provide webhook URL information for admin"""
    event_obj = get_object_or_404(Event, slug=event, organizer__slug=organizer)
    
    webhook_url = request.build_absolute_uri(
        eventreverse(event_obj, 'plugins:pretix_paystack:webhook')
    )
    
    return HttpResponse(f"""
    <div class="alert alert-info">
        <h4>Paystack Webhook Configuration</h4>
        <p>Configure this URL in your Paystack dashboard:</p>
        <code>{webhook_url}</code>
        <p>Make sure to set the webhook secret in the plugin settings.</p>
    </div>
    """)
