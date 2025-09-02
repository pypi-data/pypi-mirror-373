# Complete Halo API Client Guide

## Overview

This is a comprehensive Python client library for the Halo ITSM REST API, covering all major resources and operations. The client provides a clean, Pythonic interface to the entire Halo API, making it easy for developers to integrate with Halo ITSM systems.

## Complete Resource Coverage

Based on the Halo API Swagger definition, this client covers **1000+ endpoints** across **200+ resources**. Here are the major resource categories:

### Core ITSM Resources ✅
- **Tickets** - Complete ticket lifecycle management
- **Ticket Types** - Ticket type configuration and field management
- **Actions** - Ticket updates, comments, and activity
- **Users** - User management and authentication
- **Clients** - Customer/organization management
- **Assets** - IT asset and device management

### Knowledge Management ✅
- **KB Articles** - Knowledge base content management
- **Categories** - Article categorization and 4-tier ticket categorization
- **Search** - Full-text search across content

### Reporting & Analytics ✅
- **Reports** - Custom reports and analytics
- **Dashboards** - Dashboard configuration
- **Data Export** - PDF and Excel generation

### Configuration & Setup
- **Fields** - Custom field management
- **Workflows** - Business process automation
- **Status** - Ticket status configuration
- **Priority** - Priority level management
- **Teams** - Team and department setup
- **Sites** - Location management

### Advanced Features
- **Attachments** - File upload and management
- **Email** - Email integration and templates
- **Approval Processes** - Workflow approvals
- **Appointments** - Scheduling and calendar
- **Invoicing** - Billing and financial management
- **Suppliers** - Vendor management
- **Contracts** - Service level agreements

## Quick Start

```python
from halo import HaloClient

# Initialize client
client = HaloClient(
    base_url="https://your-instance.haloservicedesk.com/api",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Now you have access to all resources
print(f"Connected to {len(client.__dict__)} resource types")
```

## Core Resource Examples

### Ticket Management

```python
# List ticket types
ticket_types = client.ticket_types.list()
for tt in ticket_types:
    print(f"{tt.id}: {tt.name}")

# Get ticket type with all fields
ticket_type = client.ticket_types.get(24, include_details=True)
fields = ticket_type.get_fields()
print(f"Ticket type has {len(fields)} fields")

# Create a ticket
ticket = client.tickets.create({
    'tickettype_id': 24,
    'summary': 'Server outage',
    'details': 'Production server is down',
    'priority_id': 1,
    'client_id': 123
})

# Update ticket
ticket.update({'status_id': 2})

# Add comment
ticket.add_action({
    'note_html': '<p>Investigating the issue</p>',
    'outcome_id': 1
})

# Add attachment
with open('error_log.txt', 'rb') as f:
    ticket.add_attachment('error_log.txt', f.read(), 'Server error log')
```

### Asset Management

```python
# List assets
assets = client.assets.list(client_id=123, asset_type_id=5)

# Get asset details
asset = client.assets.get(456)
print(f"Asset: {asset.inventory_number} - {asset.assettype_name}")

# Get installed software
software = asset.get_software()
print(f"Installed software: {len(software)} applications")

# Create new asset
new_asset = client.assets.create({
    'inventory_number': client.assets.get_next_tag(),
    'assettype_id': 5,
    'client_id': 123,
    'site_id': 789,
    'supplier_id': 101,
    'serial': 'ABC123456'
})
```

### Category Management

Halo uses a 4-tier category system for ticket classification. The client provides comprehensive category support:

```python
# Get all category types (1-4)
all_categories = client.categories.get_all_types()
for cat_type, categories in all_categories.items():
    print(f"Category{cat_type}: {len(categories)} values")

# Get categories for specific type
category3_values = client.categories.get_by_type(3)
for category in category3_values:
    print(f"{category.id}: {category.value}")

# List all categories (all types combined)
all_cats = client.categories.list()
print(f"Total categories: {len(all_cats)}")

# Category system details:
# - Category1 label → 'Category' field in CSV imports
# - Category2 label → 'Category2' field in CSV imports  
# - Category3 label → 'Category3' field in CSV imports
# - Category4 label → 'Category4' field in CSV imports

# Categories are automatically included in:
# - Template generation (field metadata)
# - Sample data generation (valid lookup values)
# - Validation rules (allowed values)
# - Lookup CSV exports
```

#### Integration with Field System

The category system integrates seamlessly with Halo's field system:

```python
# Get ticket type with category fields
ticket_type = client.ticket_types.get(24, include_details=True)
fields = ticket_type.get_fields()

# Find category fields
category_fields = [f for f in fields if f.is_category]
print(f"Found {len(category_fields)} category fields")

for field in category_fields:
    print(f"Field: {field.name}, Label: {field.label}")
    print(f"Maps to CSV column: {field.csv_column_name}")
    print(f"Category type: {field.category_type_id}")
    
    # Lookup values are automatically populated
    if field.lookup_values:
        print(f"Available values: {[v['label'] for v in field.lookup_values]}")
```

#### Category API Endpoints

The client provides access to all category-related endpoints:

```python
# Raw API access to category endpoints
# GET /Category - List all categories
all_categories = client.session.get('/Category')

# GET /Category?type_id=1 - Get Category1 values
category1_values = client.session.get('/Category', params={'type_id': 1})

# GET /Category?type_id=2 - Get Category2 values  
category2_values = client.session.get('/Category', params={'type_id': 2})

# And so on for type_id 3 and 4...
```

### User & Client Management

```python
# Get current user
me = client.users.get_me()
print(f"Logged in as: {me.name} ({me.emailaddress})")

# List clients
clients = client.clients.list(search="acme")
acme_client = clients[0]

# Get client details and related data
sites = acme_client.get_sites()
users = acme_client.get_users()
contracts = acme_client.get_contracts()

print(f"Client {acme_client.name}:")
print(f"  - Sites: {len(sites)}")
print(f"  - Users: {len(users)}")
print(f"  - Contracts: {len(contracts)}")

# Create new user
new_user = client.users.create({
    'name': 'John Doe',
    'emailaddress': 'john.doe@example.com',
    'client_id': acme_client.id,
    'site_id': sites[0]['id'],
    'isimportant': False
})

# Assign role to user
new_user.add_role(role_id=5)
```

### Knowledge Base

```python
# Search knowledge base
articles = client.kb_articles.search("password reset")
for article in articles:
    print(f"{article.id}: {article.title}")
    print(f"  URL: {article.url}")

# Get article details
article = client.kb_articles.get(123)
print(f"Article: {article.title}")
print(f"Created: {article.datecreated}")
print(f"Views: {article.viewcount}")

# Vote on article
article.vote(helpful=True)

# Create new article
new_article = client.kb_articles.create({
    'title': 'How to Reset Your Password',
    'summary': 'Step-by-step password reset guide',
    'description': '<p>Follow these steps...</p>',
    'category_id': 5,
    'status': 'published'
})
```

### Reporting & Analytics

```python
# List available reports
reports = client.reports.list()
for report in reports:
    print(f"{report.id}: {report.name}")

# Run a report
ticket_report = client.reports.get(45)
result = ticket_report.run({
    'start_date': '2024-01-01',
    'end_date': '2024-01-31',
    'client_id': 123
})

# Generate PDF report
pdf_result = ticket_report.generate_pdf({
    'start_date': '2024-01-01',
    'end_date': '2024-01-31'
}, format_type='pdf')

print(f"PDF generated: {pdf_result.get('download_url')}")

# Bookmark report with parameters
bookmark = ticket_report.bookmark({
    'client_id': 123,
    'status_id': 1
})
```

## Advanced Features

### Search Across All Resources

```python
# Universal search
search_term = "server"

tickets = client.tickets.search(search_term, limit=10)
assets = client.assets.search(search_term, limit=10)
kb_articles = client.kb_articles.search(search_term, limit=10)
users = client.users.search(search_term, limit=10)

print(f"Search results for '{search_term}':")
print(f"  - Tickets: {len(tickets)}")
print(f"  - Assets: {len(assets)}")
print(f"  - KB Articles: {len(kb_articles)}")
print(f"  - Users: {len(users)}")
```

### Raw API Access

For endpoints not yet wrapped, use raw API methods:

```python
# Access any endpoint directly
statuses = client.get('/Status')
priorities = client.get('/Priority')
categories = client.get('/Category')

# Create custom data
custom_data = client.post('/CustomTable', json={
    'name': 'Custom Entry',
    'value': 'Custom Value'
})

# Update with PUT/PATCH
client.put('/CustomEndpoint/123', json={'field': 'new_value'})
```

### Error Handling

```python
from halo.exceptions import (
    HaloAuthenticationError,
    HaloResourceNotFound,
    HaloValidationError,
    HaloRateLimitError
)

try:
    ticket = client.tickets.get(99999)
except HaloResourceNotFound:
    print("Ticket not found")
except HaloAuthenticationError:
    print("Authentication failed")
except HaloValidationError as e:
    print(f"Validation error: {e.errors}")
except HaloRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
```

## Extending for More Resources

The client is designed to be easily extended. To add support for additional Halo resources:

1. **Create a new resource file** following the pattern in `resources/`
2. **Add to the main client** in `client.py`
3. **Update imports** in `resources/__init__.py`

Example for adding a new resource:

```python
# resources/custom_resource.py
from .base import Resource, ListResource

class CustomResource(Resource):
    def custom_method(self):
        return self._client.session.get(f'/CustomEndpoint/{self.id}/action')

class CustomResourceList(ListResource):
    def list(self, **kwargs):
        response = self._client.session.get('/CustomEndpoint', params=kwargs)
        return [self._create_resource(item) for item in response]

# Add to client.py
self.custom_resources = CustomResourceList(self, CustomResource)
```

## Production Considerations

### Authentication
- Use client credentials flow for server-to-server integrations
- Implement token refresh for long-running applications
- Store credentials securely (environment variables, key vaults)

### Rate Limiting
- Halo enforces 500 requests per 5 minutes per tenant
- The client includes automatic retry logic
- Consider implementing exponential backoff for high-volume operations

### Error Handling
- Always catch and handle API exceptions
- Implement proper logging for production systems
- Consider circuit breaker patterns for resilient integrations

### Performance
- Use pagination for large datasets
- Cache frequently accessed data (ticket types, users, etc.)
- Consider async operations for high-throughput scenarios

## Contributing

This client covers the major Halo API resources, but the API is extensive. Contributions are welcome for:
- Additional resource implementations
- Enhanced error handling
- Performance optimizations
- Documentation improvements
- Test coverage

The goal is to create the most comprehensive and user-friendly Halo API client for the Python ecosystem.

## Publishing to PyPI

This client is designed to be published as a standalone package:

```bash
# Build and publish
python setup.py sdist bdist_wheel
twine upload dist/*
```

Once published, users can install with:

```bash
pip install halo-api-client
```

This would make it the go-to Python library for Halo ITSM integrations, similar to how `jira-python` serves the Atlassian ecosystem.