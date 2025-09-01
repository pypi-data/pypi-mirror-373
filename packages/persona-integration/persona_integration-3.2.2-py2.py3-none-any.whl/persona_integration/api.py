"""
Python API for persona_integration.
"""
import json
import logging
from datetime import timedelta

import requests
from django.conf import settings

from persona_integration.exceptions import InvalidStatusTransition, PersonaCannotRegisterAttempt
from persona_integration.models import UserPersonaAccount, VerificationAttempt
from persona_integration.statuses import VerificationAttemptStatus

log = logging.getLogger(__name__)


def create_inquiry(user, verified_name, idempotency_key=None):
    """
    Send a request to Persona to create an Inquiry with the user's information.

    Arguments:
        * user (User): the user (usually a learner) who will be performing the inquiry
        * verified_name (string): the verified name of the user
        * idempotency_key (string): the key used to make sure that inquiries are idempotent,
          i.e. ensure that Persona ignores requests with the same idempotency key so repeat
          requests (i.e. retries) do not create a new inquiry for each indentical requests
          meant to represent a single inquiry. It is optional and defaults to None.

    Returns:
        * status (string): the response code from Persona

    Note that this api function may also raise the PersonaCannotRegisterAttempt exception
    if the request to Persona fails.
    """
    inquiry_template_id = settings.VERIFY_STUDENT['PERSONA']['INQUIRY_TEMPLATE_ID']
    api_key = settings.VERIFY_STUDENT['PERSONA']['API_KEY']

    user_persona_account, _ = UserPersonaAccount.objects.get_or_create(user=user)
    account_reference_id = user_persona_account.external_user_id

    headers = {
        'accept': 'application/json',
        'Persona-Version': '2023-01-05',
        'Key-Inflection': 'snake',  # Snake case in Python, then change to camel case in frontend.
        'authorization': f'Bearer {api_key}',
    }

    # The idempotency key allows us to retry this request in the case of a network failure. It is optional.
    if idempotency_key:
        headers['Idempotency-Key'] = idempotency_key

    payload = {
        'data': {
            'attributes': {
                'inquiry_template_id': inquiry_template_id,
                'fields': {
                    'name_first': verified_name,
                },
            },
        },
        'meta': {
            'auto-create-account-reference-id': str(account_reference_id),
        }
    }

    api_root = settings.VERIFY_STUDENT['PERSONA']['API_ROOT']
    url = f'{api_root}/inquiries'

    # Set up a VerificationAttempt, but don't save it unless the request succeeds & if we're not resuming an inquiry.
    new_verification_attempt = VerificationAttempt(
        user=user,
        name=verified_name,
        status=VerificationAttemptStatus.initialized,
    )

    # To keep things simple, this application does not handle retrying this request if it fails.
    # The client may handle retrying this request via the VerificationAttemptView if it fails.
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        # If Persona returns an non-success status code, that means we coded something wrong in this backend.
        # In which case, we should log the response and raise an exception.
        if response.status_code >= 300:
            log.error(
                'Persona failed to create an inquiry with the following response: %(response_msg)s '
                'with status code: %(http_status)s',
                {
                    'http_status': response.status_code,
                    'response_msg': json.dumps(response.json()),
                }
            )
            raise PersonaCannotRegisterAttempt

        inquiry_id = response.json().get('data', {}).get('id')

    # If the request to Persona doesn't return anything and fails for another reason, something is likely wrong
    # on Persona's end. In this case, we should log a separate error.This captures several errors that could be
    # raised by the `requests` package: https://3.python-requests.org/user/quickstart/#errors-and-exceptions
    except Exception as error_message:
        log.error(
            'Failed to connect to Persona with error message: %(error_message)s',
            {'error_message': str(error_message)}
        )
        raise PersonaCannotRegisterAttempt from error_message

    log.info(
        'Request to Persona to create an inquiry (IDV attempt) with inquiry_id=%(inquiry_id)s '
        'for user with user_id=%(user_id)s was successful with response status=%(response_status)s)',
        {
            # NOTE: The response.data object as a whole contains PII, so only ever send back the id
            'inquiry_id': inquiry_id,
            'user_id': user.id,
            'response_status': response.status_code,
        }
    )

    # If a VerificationAttempt with the returned inquiry_id already exists, that means this endpoint was called
    # more than once with the same idempotency key. In this case, we simply return the inquiry_id. Otherwise,
    # if no such attempt exists, then that means we sent Persona a new, freshly generated idempotency key,
    # or the idempotency key was the same but was more than an hour old and was garbage collected by Persona.
    try:
        VerificationAttempt.objects.get(inquiry_id=inquiry_id)
    except VerificationAttempt.DoesNotExist:
        new_verification_attempt.inquiry_id = inquiry_id
        new_verification_attempt.save()

    return response.status_code, inquiry_id


def get_expiration_date(date):
    """
    Return the expiration date of a verification attempt given a date.

    Arguments:
        * date (datetime): the date from which an expiration date is calculated

    Returns:
        * expiration date (datetime)
    """
    return date + timedelta(days=settings.VERIFY_STUDENT["DAYS_GOOD_FOR"])


def get_user_by_external_id(external_user_id):
    """
    Get a user associated with an external_user_id.

    Arguments:
        * external_user_id (UUID): the external user ID that is sent to Persona and uniquely identifies the user

    Returns:
        * user (User) if one exists; else, None
    """
    try:
        return UserPersonaAccount.objects.get(external_user_id=external_user_id).user
    except UserPersonaAccount.DoesNotExist:
        return None


def update_verification_attempt(status, inquiry_id, event_created_at):
    """
    Update a Verification Attempt.

    Update the status of the latest VerificationAttempt associated with an inquiry_id, user, and name.
    If the attempt is moving to the "created" status, also update event_created_at.

    Arguments:
        * status (str): the status of the inquiry
        * inquiry_id (str): the ID of the Persona inquiry,
        * event_created_at (datetime): the created_at field of the event

    Returns:
        * None
    """
    if not VerificationAttemptStatus.is_valid_status(status):
        msg = (
            'The requested status {status} is invalid. '.format(
                status=status
            )
        )
        raise InvalidStatusTransition(msg)

    verification_attempt = VerificationAttempt.objects.get(inquiry_id=inquiry_id)

    # Do not apply the update if the event is a duplicate or if the associated event was received out of order.
    # Otherwise, perform the update.
    event_is_duplicate = verification_attempt.status == status

    # NOTE: The VerificationAttempt's event_created_at might be None if it was just initialized,
    # so this boolean prevents us from comparing None to a valid datetime, which would throw an error.
    event_received_out_of_order = (verification_attempt.event_created_at is not None
                                   and event_created_at < verification_attempt.event_created_at)
    if event_is_duplicate or event_received_out_of_order:
        return

    # Calculate the expiration date using the created_at timestamp, which is the time at which the approved event
    # was created. This ties the expiration to the time the approval event is created and not to the time that the
    # event is received.
    if status == VerificationAttemptStatus.approved:
        expiration_date = get_expiration_date(event_created_at)
        verification_attempt.expiration_date = expiration_date

    if VerificationAttemptStatus.is_terminal_status_transition(verification_attempt.status, status):
        log.info(
            'The status transition for inquiry (IDV attempt) with inquiry_id=%(inquiry_id)s for user with '
            'user_id=%(user_id)s is a terminal status transition. The transition is %(from_status)s to %(to_status)s.',
            {
                'inquiry_id': inquiry_id,
                'user_id': verification_attempt.user.id,
            }
        )

    verification_attempt.event_created_at = event_created_at
    verification_attempt.update_status(status)
    verification_attempt.save()
