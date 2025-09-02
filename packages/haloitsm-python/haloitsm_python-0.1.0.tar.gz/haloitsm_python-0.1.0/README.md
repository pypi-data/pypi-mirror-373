# haloitsm-python

This is a Python library for the HaloITSM tool. It is written and maintained by BDQ.cloud, a Halo partner as a useful resource for the HaloITSM community. This library is not supported or endorsed by Halo.

# Halo API Client

A clean, Pythonic client library for the Halo ITSM REST API. This library provides a simple interface for interacting with Halo while maintaining a clear separation between API operations and business logic.

## Features

- **Clean API**: Intuitive, Pythonic interface similar to popular clients like `jira-python`
- **Automatic Authentication**: Handles OAuth2 token management and refresh
- **Resource-based Design**: Work with tickets, ticket types, and fields as Python objects
- **Error Handling**: Comprehensive exception hierarchy for different error scenarios
- **Retry Logic**: Built-in retry mechanisms for transient failures
- **Type Hints**: Full type hint coverage for better IDE support

## Installation

```bash
pip install halo-api-client
```

## Quick Start

```python
from halo import HaloClient

# Initialize the client
client = HaloClient(
    base_url="https://your-instance.haloservicedesk.com/api",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# List all ticket types
for ticket_type in client.ticket_types.list():
    print(f"{ticket_type.id}: {ticket_type.name}")

# Get a specific ticket type with field details
ticket_type = client.ticket_types.get(24, include_details=True)
fields = ticket_type.get_fields()

# Create a new ticket
ticket = client.tickets.create({
    'tickettype_id': 24,
    'summary': 'Server down',
    'details': 'Production server is not responding'
})

# Update the ticket
ticket.update({'status_id': 2})

# Add a comment
ticket.add_action({
    'note_html': '<p>Looking into this issue</p>',
    'outcome_id': 1
})
```

## Authentication

The client supports multiple authentication methods:

### Client Credentials (Recommended for server-to-server)

```python
client = HaloClient(
    base_url="https://your-instance.haloservicedesk.com/api",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

### Username/Password

```python
client = HaloClient(
    base_url="https://your-instance.haloservicedesk.com/api",
    client_id="your-client-id",
    username="user@example.com",
    password="your-password"
)
```

### Existing Token

```python
client = HaloClient(
    base_url="https://your-instance.haloservicedesk.com/api",
    token="existing-access-token",
    refresh_token="existing-refresh-token"
)
```

## Working with Resources

### Ticket Types

```python
# List ticket types with filters
ticket_types = client.ticket_types.list(
    show_inactive=False,
    can_create_only=True
)

# Get a specific ticket type
ticket_type = client.ticket_types.get(24)

# Get fields for a ticket type
ticket_type = client.ticket_types.get(24, include_details=True)
fields = ticket_type.get_fields()

# Access field properties
for field in fields:
    print(f"{field.name}: {field.field_type}")
    if field.is_mandatory:
        print("  - Required field")
    if field.lookup_values:
        print("  - Lookup values:", field.lookup_values)
```

### Tickets

```python
# Search tickets
tickets = client.tickets.search("server down", limit=10)

# List tickets with filters
tickets = client.tickets.list(
    ticket_type_id=24,
    status_id=1,
    page_size=50
)

# Get a specific ticket
ticket = client.tickets.get(12345)

# Create a ticket
ticket = client.tickets.create({
    'tickettype_id': 24,
    'summary': 'New issue',
    'details': 'Issue description',
    'priority_id': 3
})

# Update a ticket
ticket.update({
    'status_id': 2,
    'summary': 'Updated summary'
})

# Add attachments
ticket.add_attachment(
    filename="screenshot.png",
    file_content=image_bytes,
    description="Error screenshot"
)
```

## Error Handling

The client provides specific exceptions for different error scenarios:

```python
from halo import (
    HaloAuthenticationError,
    HaloResourceNotFound,
    HaloValidationError,
    HaloRateLimitError
)

try:
    ticket = client.tickets.get(99999)
except HaloResourceNotFound as e:
    print(f"Ticket not found: {e}")
except HaloAuthenticationError as e:
    print(f"Authentication failed: {e}")
except HaloValidationError as e:
    print(f"Validation error: {e.errors}")
except HaloRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
```

## Advanced Usage

### Raw API Access

For endpoints not yet wrapped by the client:

```python
# Make raw API calls
response = client.get('/custom/endpoint', params={'filter': 'value'})
response = client.post('/custom/endpoint', json={'data': 'value'})
```

### Custom Session Configuration

```python
client = HaloClient(
    base_url="https://your-instance.haloservicedesk.com/api",
    client_id="your-client-id",
    client_secret="your-client-secret",
    timeout=60,  # Request timeout in seconds
    max_retries=5  # Maximum retry attempts
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
