"""
Database models for persona_integration.
"""
import logging
import uuid

from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel

from persona_integration.exceptions import InvalidStatusTransition
from persona_integration.statuses import VerificationAttemptStatus

logger = logging.getLogger(__name__)


class UserPersonaAccount(TimeStampedModel):
    """
    This model contains Persona related user information and maps to User.

    ... no_pii: This model has no PII.
    """

    # external reference to be shared between edx and Persona
    external_user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)


class VerificationAttempt(TimeStampedModel):
    """
    Information about a verification attempt (i.e. a Persona inquiry).

    .. pii: Stores full name of a user.
    .. pii_types: name
    .. pii_retirement: local_api

    """

    # Because the edx-platform verify_student.VerificationAttempt model has the same name as this model and also has a
    # foreign key to the User model, the default reverse accessors for this foreign key relationship and that foreign
    # key relationship have the same name (User.verificationattempt_set), resulting in a conflict. For this reason, we
    # set an explicit related_name value here to resolve the conflict.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='persona_verificationattempt_set'
    )

    # The name field refers to the learner's verified name as submitted by the learner. It represents the name that the
    # learner stated will appear on their ID. The statuses approved and declined reflect whether or not Persona verified
    # that this name appears on the learner's ID.
    name = models.CharField(max_length=255)

    STATUS_CHOICES = [
        VerificationAttemptStatus.initialized,
        VerificationAttemptStatus.created,
        VerificationAttemptStatus.pending,
        VerificationAttemptStatus.expired,
        VerificationAttemptStatus.approved,
        VerificationAttemptStatus.declined,
    ]

    status = models.CharField(max_length=64, choices=[(status, status) for status in STATUS_CHOICES])

    expiration_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    # The inquiry_id field refers to the ID of the inquiry in Persona. This value is used to uniquely refer to an
    # inquiry in Persona.
    inquiry_id = models.CharField(max_length=255, unique=True, blank=True, null=True)

    # The event_created_at field refers to the created_at field of the latest event received and processed via webhook
    # for this attempt. It is used to determine when events are received out of order.
    event_created_at = models.DateTimeField(null=True)

    # The platform_verification_attempt_id refers to the id of an edx-platform verify_student.VerificationAttempt model
    # instance. The reason we store this is so that we have access to the model instance id, which is needed to make
    # calls to the edx-platform update API.
    # The decision to store the id and not a traditional foreign key is documented in an ADR in this repository.
    platform_verification_attempt_id = models.PositiveIntegerField(null=True)

    def update_status(self, status):
        """
        Update the VerificationAttempt status.

        Arguments:
            * status (str): the new status

        Returns:
            * None

        Raises:
            * InvalidStatusTransition if the status transition is not valid
        """
        is_valid = VerificationAttemptStatus.is_valid_status_transition(self.status, status)

        if is_valid:
            self.status = status
            self.save()
        else:
            msg = (
                'The requested status transition is invalid. ' +
                'The current status is {from_status}, and the new status is {to_status}.'.format(
                    from_status=self.status, to_status=status
                )
            )
            raise InvalidStatusTransition(msg)
