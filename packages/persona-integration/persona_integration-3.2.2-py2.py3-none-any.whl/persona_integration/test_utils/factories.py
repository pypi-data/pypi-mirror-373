"""
Factories for persona_integration tests.
"""

from datetime import timezone

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from persona_integration.models import UserPersonaAccount, VerificationAttempt
from persona_integration.statuses import VerificationAttemptStatus


class UserFactory(DjangoModelFactory):
    """
    Factory to create User objects.
    """

    class Meta:
        model = get_user_model()
        django_get_or_create = (
            'email',
            'username',
        )

    _DEFAULT_PASSWORD = 'test'

    username = factory.Sequence('user{}'.format)
    email = factory.Sequence('user+test+{}@edx.org'.format)
    password = factory.PostGenerationMethodCall('set_password', _DEFAULT_PASSWORD)
    is_superuser = False
    is_staff = False


class UserPersonaAccountFactory(DjangoModelFactory):
    """
    Factory to crate UserPersonaAccount objects.
    """

    class Meta:
        model = UserPersonaAccount

    user = factory.SubFactory(UserFactory)
    external_user_id = factory.Faker('uuid4')


class VerificationAttemptFactory(DjangoModelFactory):
    """
    Factory to create VerificationAttempt objects.
    """
    class Meta:
        model = VerificationAttempt

    user = factory.SubFactory(UserFactory)
    name = factory.Faker('name')
    status = VerificationAttemptStatus.created
    expiration_date = None
    inquiry_id = factory.Sequence('inquiry-id-{}'.format)
    event_created_at = factory.Faker('date_time', tzinfo=timezone.utc)
