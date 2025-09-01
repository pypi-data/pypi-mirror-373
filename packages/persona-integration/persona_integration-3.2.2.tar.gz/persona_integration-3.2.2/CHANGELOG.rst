Change Log
##########

..
   All enhancements and patches to persona_integration will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
**********

3.2.1
*****
* Added support for Django 5.2

3.2.0 2024-12-18
****************
* Removed the requirement on Python 3.12 or greater. 
* Added Python 3.11 to the matrix for the Python CI tests step.
* Added Python 3.11 to the tox envlist.

3.1.0 2024-12-18
****************
* Updated the is_valid_status_transition API method to allow terminal status transitions.

3.0.0  2024-10-25
*****************

Added
=====
* Upgraded to  ``Python 3.12``
* Dropped support for ``Python<3.12``

2.2.0  2024-10-10
*****************

Added
=====
* Fix bug regarding mapping of status between this backend's VerificationAttempt model and the one in the LMS (The definitions of the "pending" status were different between the two models).

2.1.0  2024-10-09
*****************

Added
=====
* Fix bug preventing VerificationAttempt model from being synchronized to the LMS.
* Add VerificationAttempt.platform_verification_attempt_id field to admin.

2.0.4 - 2024-10-07
******************

Added
=====
* Fix errors in UserPersonaAccount and VerificationAttempt Django admin forms.

2.0.3 - 2024-09-27
******************

Added
=====
* Removed undesired email-related variables in Persona payload.

2.0.2 - 2024-09-27
******************

Added
=====
* Add __init__.py to signals package.

2.0.1 - 2024-09-26
******************

Added
=====
* Add user persona account model and admin.
* Add VerificationAttempt model and admin to store Persona attempts.
* Add a view to handle Persona webhooks.
* Add a create inquiry view.
* Add field for edx-platform VerificationAttempt model id.
* Add event listener for user retirement signal.
* Update name of reverse accessor on User model to resolve conflict.
* Modify VerificationAttemptView to return inquiry_id.
* Make several fixes to the VerificationAttemptView view and the create_inquiry API method.
* Replace field `verified_name` with `name_first` when communicating with persona.
* Fix an error on the payload for create_inquiry API call to Persona.
* Sync updates to VerificationAttempt model.

2.0.0 - 2024-09-25
******************

Added
=====
* Bump version.

1.0.0 - 2024-07-18
******************

Added
=====

* Initial release.
* Setup repo using template.

0.1.0 - 2024-07-18
******************

Added
=====

* First release on PyPI.
