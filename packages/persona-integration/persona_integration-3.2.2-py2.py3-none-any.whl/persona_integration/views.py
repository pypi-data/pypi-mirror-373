"""
Views for persona_integration.
"""
import hmac
import logging
from collections import namedtuple

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from persona_integration.api import create_inquiry, get_user_by_external_id, update_verification_attempt
from persona_integration.exceptions import InvalidStatusTransition, PersonaCannotRegisterAttempt
from persona_integration.utils import parse_basic_iso_date_to_full_date

log = logging.getLogger(__name__)


class VerificationAttemptView(APIView):
    """
    When called, create an inquiry for a user who needs to undergo the ID Verification process.

    Persona strongly recommended that we preemptively create an inquiry on their backend before
    a learner accesses the Person application to perform IDV via our own backend call,
    because calls to their inquiry endpoint cannot come from the browser.

    Accepts:
        * [POST]

    This class only supports POST requests.
    """

    authentication_classes = (SessionAuthentication, JwtAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Receive and pass along requests to create an inquiry in Persona.

        Paths:
        * persona/create_inquiry

        Returns:
        * 201: The request to create an inquiry in Persona was successful.
        (NOTE: This backend will still receive a request in the WebhookView to confirm that an inquiry was created.)
        * 400: The request data is invalid.
        * 500: Failed to create Persona Inquiry from this backend.
        """
        user = request.user
        verified_name = request.data.get('verified_name')
        idempotency_key = request.data.get('idempotency_key')

        # If there is a bad request from the UI to this backend, return 400:
        if None in [verified_name]:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'detail': (
                    'Bad request to persona-integration. verified_name is a required field.'
                )}
            )

        try:
            _, inquiry_id = create_inquiry(user, verified_name, idempotency_key)
        # If the request from this backend to Persona fails, return 500
        except PersonaCannotRegisterAttempt:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_201_CREATED, data={'inquiry_id': inquiry_id})


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(APIView):
    """
    Receive and process webhook requests from Persona, corresponding to lifecycle events.

    Currently, this view only processes inquiry related events, as configured in the Persona dashboard.

    Accepts:
        * [POST]

    This class only supports POST requests.
    """

    Event = namedtuple('Event', [
        'webhook_type',
        'event_id',
        'payload_type',
        'inquiry_id',
        'inquiry_status',
        'created_at',
        'reference_id',
    ])

    def validate_request_signature(self, request, webhook_secret):
        """
        Return whether the Persona-Signature request header is valid.

        This function supports keys in the process of rotation.

        The format of the Persona-Signature header is as follows.

        t=<timestamp>, v1=<signature>

        If the header has two signatures, which will happen if the keys are in the process of rotatin, the format of the
        Persona-Signature header is as follows.

        t=<timestamp>, v1=<signature_new> v1=<signature_old>

        Arguments:
            * request (Request): request object
            * webhook_secret (str): Persona webhook secret used to generate the HMAC

        Returns:
            * True if the signature is valid; else, False
        """
        timestamp, signatures = list(request.headers['Persona-Signature'].split(','))

        timestamp = timestamp.split('t=')[1]
        digest = hmac.new(
            webhook_secret.encode(), (timestamp + '.' + request.body.decode('utf-8')).encode(), 'sha256'
        ).hexdigest()

        if len(signatures.split(' ')) > 1:
            signature_new, signature_old = [value.split('v1=')[1] for value in signatures.split(' ')]
            if hmac.compare_digest(signature_new, digest) or hmac.compare_digest(signature_old, digest):
                return True
        else:
            signature = signatures.split('v1=')[1]
            signature = request.headers['Persona-Signature'].split(',')[1].split('=')[1]
            if hmac.compare_digest(signature, digest):
                return True

        return False

    def extract_event_data(self, request):
        """
        Extract relevant data from the event.

        Arguments:
            * request (Request): request object

        Returns:
            * an instance of the Event namedtuple; False if event data is missing or cannot be extracted
        """
        try:
            data = request.data['data']
            webhook_type = data['type']
            event_id = data['id']
            payload_type = data['attributes']['payload']['data']['type']

            inquiry_id = data['attributes']['payload']['data']['id']
            inquiry_status = data['attributes']['payload']['data']['attributes']['status']
            reference_id = data['attributes']['payload']['data']['attributes']['reference_id']

            created_at = parse_basic_iso_date_to_full_date(data['attributes']['created_at'])

            return WebhookView.Event(
                webhook_type=webhook_type,
                event_id=event_id,
                payload_type=payload_type,
                inquiry_id=inquiry_id,
                inquiry_status=inquiry_status,
                created_at=created_at,
                reference_id=reference_id,
            )
        except KeyError:
            return False

    def post(self, request):
        """
        Receive and process webhook requests from Persona, corresponding to lifecycle events.

        Currently, this view only processes inquiry related events, as configured in the Persona dashboard.

        A response with a 200 status code will be returned for all valid requests (i.e. veriable signature, properly
        formed request) to ensure that Persona does not re-try the request, but only inquiry related events will be
        processed.

        Note that a signature in the Persona-Signature header is required.

        Paths:
        * persona/webhook

        Returns:
        * 200: The request was successfully handled.
        * 400: The request data is malformed or invalid.
        * 404: The request could not be authenticated.
        * 500: The server is misconfigured (e.g. the webhook secret configuration is missing).
        """
        webhook_secret = settings.VERIFY_STUDENT.get('PERSONA', {}).get('WEBHOOK_SECRET')

        if not webhook_secret:
            log.error('Persona webhook secret is missing.')
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        is_valid = self.validate_request_signature(request, webhook_secret)

        if not is_valid:
            log.error('Persona webhook signature is not valid.')
            return Response(status=status.HTTP_404_NOT_FOUND)

        event = self.extract_event_data(request)

        if not event:
            log_msg = 'Persona event is malformed and is missing required data.'

            event_id = request.data.get('id')
            if event_id:
                log_msg += 'The event ID is %s.'
                log.error(log_msg, event_id)
            else:
                log.error(log_msg)

            return Response(status=status.HTTP_400_BAD_REQUEST)

        # If the webhook data does not represent an event or is not related to an inquiry, ignore the request
        # and return a response with a 200 status to acknowledge the webhook.
        if event.webhook_type != 'event' or event.payload_type != 'inquiry':
            return Response(status=status.HTTP_200_OK)

        # Log the event for auditability. Although we have set up inquiry blocklists to filter out any extraneous PII,
        # we still avoid logging the entire event object to ensure that we do not accidentally log any additional PII.
        log_msg = (
            'Received event from Persona. '
            'event ID: %s, created at: %s, inquiry ID: %s, reference_id: %s, inquiry status: %s',
        )
        log.info(
            log_msg,
            event.event_id,
            event.created_at,
            event.inquiry_id,
            event.reference_id,
            event.inquiry_status,
        )

        user = get_user_by_external_id(event.reference_id)

        if not user:
            log_msg = (
                'The reference_id in the Persona event is not associated with a user. '
                'The event ID is %s.'
            )
            log.error(log_msg, event.event_id)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            update_verification_attempt(
                event.inquiry_status,
                event.inquiry_id,
                event.created_at,
            )
        except InvalidStatusTransition as e:
            # Theoretically, this should not occur, because out of order events are disregarded, and the verification
            # attempt lifecycle is unidirectional. In this case, we return a 200 to Persona to acknowledge the webhook
            # and log the case.
            log_msg = (
                'The status in the Persona event represents an invalid status transition. This should not occur. '
                'The event ID is %s. '
                'Exception: %s.'
            )
            log.warning(log_msg, event.event_id, e)

        return Response(status=status.HTTP_200_OK)
