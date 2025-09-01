"""
persona_integration Django application initialization.
"""

from django.apps import AppConfig


class PersonaIntegrationConfig(AppConfig):
    """
    Configuration for the persona_integration Django application.
    """

    name = 'persona_integration'

    plugin_app = {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'persona_integration',
                'regex': '^api/',
                'relative_path': 'urls',
            },
        }
    }

    def ready(self):
        """
        Connect signal handlers.
        """
        from persona_integration.signals import handlers  # pylint: disable=import-outside-toplevel,unused-import
