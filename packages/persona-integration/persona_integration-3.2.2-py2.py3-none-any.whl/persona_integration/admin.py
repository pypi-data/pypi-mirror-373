"""
Admin forms for persona_integration.
"""
from django.contrib import admin

from persona_integration.models import UserPersonaAccount, VerificationAttempt


@admin.register(UserPersonaAccount)
class UserPersonaAccountAdmin(admin.ModelAdmin):
    """
    Django admin form for UserPersonAccount model.
    """

    fields = ['created', 'external_user_id', 'modified', 'user',]
    list_display = ['user', 'external_user_id',]
    raw_id_fields = ['user',]
    readonly_fields = ['created', 'external_user_id', 'modified',]
    search_fields = ['external_user_id', 'user__username',]


@admin.register(VerificationAttempt)
class VerificationAttemptAdmin(admin.ModelAdmin):
    """
    Django admin form for VerificationAttempt model.
    """

    fields = [
        'created', 'event_created_at', 'expiration_date', 'inquiry_id', 'modified', 'platform_verification_attempt_id',
        'status', 'user',
    ]
    list_display = [
        'id', 'user', 'name', 'status', 'inquiry_id', 'platform_verification_attempt_id', 'created', 'modified',
        'event_created_at',
    ]
    raw_id_fields = ['user',]
    readonly_fields = ['created', 'event_created_at', 'modified', 'platform_verification_attempt_id',]
    search_fields = ['inquiry_id', 'user__username',]
