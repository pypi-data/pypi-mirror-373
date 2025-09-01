"""
URLs for persona_integration.
"""
from django.urls import path

from persona_integration import views

app_name = 'persona_integration'

urlpatterns = [
    path('persona/v1/webhook', views.WebhookView.as_view(), name='webhook'),
    path('persona/v1/inquiry', views.VerificationAttemptView.as_view(), name='create_inquiry'),
]
