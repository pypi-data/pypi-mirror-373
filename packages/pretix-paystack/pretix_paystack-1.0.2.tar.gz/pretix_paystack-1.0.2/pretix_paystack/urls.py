from django.urls import path, include

from .views import PaystackWebhookView, PaystackReturnView, PaystackReconcileView

event_patterns = [
    path('paystack/', include([
        path('webhook/', PaystackWebhookView.as_view(), name='webhook'),
        path('return/<str:order>/<str:secret>/<int:payment>/', PaystackReturnView.as_view(), name='return'),
        path('reconcile/', PaystackReconcileView.as_view(), name='reconcile'),
    ])),
]

urlpatterns = [
    path('control/event/<str:organizer>/<str:event>/paystack/', include([
        path('reconcile/', PaystackReconcileView.as_view(), name='reconcile'),
    ])),
]
