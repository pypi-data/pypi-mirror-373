"""Halo API client library.

A clean, Pythonic client for the Halo ITSM REST API.

Example:
    >>> from halo import HaloClient
    >>> 
    >>> client = HaloClient(
    ...     base_url="https://instance.haloservicedesk.com/api",
    ...     client_id="your-client-id",
    ...     client_secret="your-client-secret"
    ... )
    >>> 
    >>> # List ticket types
    >>> for ticket_type in client.ticket_types.list():
    ...     print(f"{ticket_type.id}: {ticket_type.name}")
    >>> 
    >>> # Get ticket type with fields
    >>> ticket_type = client.ticket_types.get(24, include_details=True)
    >>> fields = ticket_type.get_fields()
    >>> 
    >>> # Create and update tickets
    >>> ticket = client.tickets.create({
    ...     'tickettype_id': 24,
    ...     'summary': 'New issue',
    ...     'details': 'Description here'
    ... })
    >>> ticket.update({'status_id': 2})
"""

__version__ = "0.1.0"
__author__ = "Chris Bland"
__email__ = "cbland@bdq.cloud"

from .client import HaloClient
from .exceptions import (
    HaloError,
    HaloAuthenticationError,
    HaloAPIError,
    HaloResourceNotFound,
    HaloValidationError,
    HaloRateLimitError
)

__all__ = [
    'HaloClient',
    'HaloError',
    'HaloAuthenticationError',
    'HaloAPIError',
    'HaloResourceNotFound',
    'HaloValidationError',
    'HaloRateLimitError'
]