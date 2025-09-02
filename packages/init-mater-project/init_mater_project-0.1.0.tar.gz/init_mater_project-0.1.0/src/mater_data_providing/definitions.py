"""
This module defines definition functions.

SPDX-License-Identifier: LGPL-3.0-or-later
"""

from email_validator import validate_email

from .validations import _validate_string


def metadata_definition(link: str, source: str, project: str) -> dict[str, str]:
    """Returns a dictionary with all the keys necessary for the mater database metadata table schema.

    :param link: Link to find the raw dataset
    :type link: str
    :param source: Source name
    :type source: str
    :param project: Name of the project you are working on
    :type project: str
    :return: One metadata table entry
    :rtype: dict[str, str]
    :raises TypeError: If any parameter is not a string
    :raises ValueError: If any parameter is None or only whitespace

    Examples
    --------
    Complete example with metadata definition:

    **Basic metadata creation:**

    .. code-block:: python

        >>> metadata = metadata_definition(
                "https://data.gov.fr/transport-dataset",
                "French Transport Ministry",
                "EU Vehicle Analysis 2024"
            )
        >>> print(metadata)
        {'link': 'https://data.gov.fr/transport-dataset', 'source': 'French Transport Ministry', 'project': 'EU Vehicle Analysis 2024'}
    """
    # validation functions
    args = locals()
    for arg in args:
        _validate_string(arg)

    return args


def provider_definition(
    first_name: str, last_name: str, email_address: str
) -> dict[str, str]:
    """Returns a dictionary with all the keys necessary for the mater database provider table schema.

    :param first_name: Your first name
    :type first_name: str
    :param last_name: Your last name
    :type last_name: str
    :param email_address: Your email address
    :type email_address: str
    :return: One provider table entry
    :rtype: dict[str, str]
    :raises TypeError: If any parameter is not a string
    :raises ValueError: If any parameter is invalid (empty names, malformed email)

    Examples
    --------
    Complete example with provider definition:

    **Basic provider creation:**

    .. code-block:: python

        >>> provider = provider_definition("John", "Doe", "john.doe@example.com")
        >>> print(provider)
        {'first_name': 'John', 'last_name': 'Doe', 'email_address': 'john.doe@example.com'}
    """
    # validation functions
    _validate_string(first_name)
    _validate_string(last_name)
    validated_email = validate_email(email_address, check_deliverability=False)

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email_address": validated_email.normalized,
    }
