"""
Signal handlers for the persona-integration plugin.
"""
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from persona_integration.models import VerificationAttempt
from persona_integration.statuses import VerificationAttemptStatus

try:
    from lms.djangoapps.verify_student.api import create_verification_attempt, update_verification_attempt
    from lms.djangoapps.verify_student.statuses import VerificationAttemptStatus as PlatformVerificationAttemptStatus
except ImportError:
    create_verification_attempt = None
    update_verification_attempt = None
    PlatformVerificationAttemptStatus = None

try:
    from openedx.core.djangoapps.user_api.accounts.signals import USER_RETIRE_LMS_MISC
except ImportError:
    # An ImportError should only be raised in tests, where the code is not running as an installation of
    # edx-platform. In this case, the import should default to a generic Signal.
    USER_RETIRE_LMS_MISC = Signal()

LMS_STATUS_MAPPING = {
    # This may seem redundant, but we must synchronize the initialized statue to the LMS because of the branching logic
    # in the on_verification_attempt_change signal handler, which determines which platform API method to call based on
    # whether the instance of the VerificationAttempt was created. Because a VerificationAttempt is always created
    # with the initialized status, in order for the branch that calls create_verification_attempt to be invoked, we must
    # synchronize the initialized status.
    VerificationAttemptStatus.initialized: (
        PlatformVerificationAttemptStatus and PlatformVerificationAttemptStatus.CREATED
    ),
    VerificationAttemptStatus.created: (
        PlatformVerificationAttemptStatus and PlatformVerificationAttemptStatus.CREATED
    ),
    VerificationAttemptStatus.pending: (
        PlatformVerificationAttemptStatus and PlatformVerificationAttemptStatus.PENDING
    ),
    VerificationAttemptStatus.approved: (
        PlatformVerificationAttemptStatus and PlatformVerificationAttemptStatus.APPROVED
    ),
    VerificationAttemptStatus.declined: (
        PlatformVerificationAttemptStatus and PlatformVerificationAttemptStatus.DENIED
    )
}


@receiver(USER_RETIRE_LMS_MISC)
def on_user_retirement(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Receives a user retirement signal and retires user data
    """
    user = kwargs.get('user')
    VerificationAttempt.objects.filter(user_id=user.id).delete()


@receiver(post_save, sender=VerificationAttempt)
def on_verification_attempt_change(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """
    Receives a verification attempt change signal and updates verification attempt status.
    """
    # NOTE: We do not update on "pending" because "pending" for Persona means that IDV in progress, which does
    # not correspond with the "pending" status in the LMS, which indicates that the user has submitted an IDV attempt
    # and blocks the user from submitting another verified name in their account settings. This prevents a user from
    # being blocked from starting a new inquiry while one is still in progress/not yet submitted.
    statuses_to_update = [
        VerificationAttemptStatus.created,
        VerificationAttemptStatus.approved,
        VerificationAttemptStatus.declined
    ]

    if instance.status in LMS_STATUS_MAPPING:
        if created:
            attempt_id = create_verification_attempt(
                user=instance.user,
                name=instance.name,
                status=LMS_STATUS_MAPPING[instance.status],
                expiration_datetime=instance.expiration_date
            )
            instance.platform_verification_attempt_id = attempt_id
            instance.save()
        else:
            if instance.status in statuses_to_update:
                update_verification_attempt(
                    attempt_id=instance.platform_verification_attempt_id,
                    name=instance.name,
                    status=LMS_STATUS_MAPPING[instance.status],
                    expiration_datetime=instance.expiration_date
                )
