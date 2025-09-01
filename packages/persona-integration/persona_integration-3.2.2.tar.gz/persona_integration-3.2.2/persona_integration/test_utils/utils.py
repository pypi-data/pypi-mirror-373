"""
Utils for test cases
"""
from unittest.mock import patch

from django.test import TestCase


class PersonaIntegrationTestCase(TestCase):
    """
    Mocks platform imports that would otherwise cause tests to fail
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()

        patch.dict(
            'persona_integration.signals.handlers.LMS_STATUS_MAPPING',
            {
                'initialized': 'created',
                'created': 'created',
                'pending': 'pending',
                'declined': 'denied',
                'approved': 'approved',
            }
        ).start()
        patch('persona_integration.signals.handlers.create_verification_attempt', return_value=1).start()
        patch('persona_integration.signals.handlers.update_verification_attempt').start()
