"""Field resource for Halo API."""
from typing import List, Dict, Any, Optional
from .base import Resource


class Field(Resource):
    """Represents a field in Halo.
    
    Fields can be system fields or custom fields associated with ticket types.
    """
    
    @property
    def is_custom(self) -> bool:
        """Check if this is a custom field."""
        return bool(self.raw.get('custom', 0))
    
    @property
    def is_mandatory(self) -> bool:
        """Check if this field is mandatory."""
        # In Halo, fields might have usage=1 for mandatory
        return self.raw.get('usage', 0) == 1 or self.raw.get('mandatory', False)
    
    @property
    def field_type(self) -> str:
        """Get the field type."""
        type_mapping = {
            -1: 'lookup',
            0: 'string',
            1: 'multiline',
            2: 'dropdown',
            3: 'date',
            4: 'datetime',
            5: 'integer',
            6: 'float',
            7: 'boolean',
            8: 'password',
            9: 'hyperlink'
        }
        field_type = self.raw.get('type', 0)
        return type_mapping.get(field_type, 'string')
    
    @property
    def lookup_values(self) -> List[Dict[str, Any]]:
        """Get lookup values if this is a lookup field.
        
        Returns:
            List of lookup values with 'id' and 'label' keys
        """
        return self.raw.get('lookup_values', [])
    
    @property
    def validation_regex(self) -> Optional[str]:
        """Get validation regex pattern if defined."""
        return self.raw.get('fieldinfo', {}).get('regex')
    
    @property
    def group_header(self) -> Optional[str]:
        """Get the group header if field is in a group."""
        return getattr(self, '_group_header', self.raw.get('group_header', ''))
    
    @property
    def is_category(self) -> bool:
        """Check if this is a category field (Category1-4)."""
        return FieldMetadata.is_category_field(self)
    
    @property
    def category_type_id(self) -> Optional[int]:
        """Get category type ID if this is a category field."""
        return FieldMetadata.get_category_type_id(self)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert field to a simplified dictionary.
        
        Returns:
            Dictionary with key field properties
        """
        return {
            'id': self.id,
            'name': self.name,
            'label': getattr(self, 'label', self.name),
            'type': self.field_type,
            'custom': self.is_custom,
            'mandatory': self.is_mandatory,
            'lookup_values': self.lookup_values,
            'validation_regex': self.validation_regex,
            'group_header': self.group_header
        }


class FieldMetadata:
    """Helper class for field metadata operations."""
    
    @staticmethod
    def is_category_field(field: Field) -> bool:
        """Check if a field is a Category field (Category1-4).
        
        Args:
            field: Field to check
            
        Returns:
            True if field is a category field
        """
        label = getattr(field, 'label', '')
        return label in ['Category1', 'Category2', 'Category3', 'Category4']
    
    @staticmethod
    def get_category_type_id(field: Field) -> Optional[int]:
        """Get the category type ID for a category field.
        
        Args:
            field: Category field
            
        Returns:
            Category type ID (1-4) or None if not a category field
        """
        label = getattr(field, 'label', '')
        mapping = {
            'Category1': 1,
            'Category2': 2,
            'Category3': 3,
            'Category4': 4
        }
        return mapping.get(label)
    
    @staticmethod
    def extract_fields_from_ticket_type(ticket_type_data: Dict[str, Any]) -> List[Field]:
        """Extract and flatten fields from ticket type response.
        
        Args:
            ticket_type_data: Raw ticket type data with fields
            
        Returns:
            List of Field resources
        """
        fields = []
        
        # Handle the actual Halo response format
        ticket_fields = ticket_type_data.get('fields', [])
        
        for field_item in ticket_fields:
            # Each field item might have a 'group' with nested fields, or be a direct field
            if 'group' in field_item and 'fields' in field_item['group']:
                # Nested group structure
                group_data = field_item['group']
                group_header = group_data.get('header', group_data.get('name', ''))
                
                for nested_field in group_data['fields']:
                    # Use the fieldinfo as the main field data
                    if 'fieldinfo' in nested_field:
                        field_data = nested_field['fieldinfo'].copy()
                        # Handle lookup values separately
                        lookup_values = []
                        if 'values' in field_data:
                            # Convert to expected format
                            lookup_values = [
                                {'id': v.get('id'), 'label': v.get('name', '')}
                                for v in field_data['values']
                            ]
                            # Remove from field_data to avoid property setter issue
                            field_data.pop('values', None)
                        
                        # Create field and add lookup values to raw data
                        field = Field(None, field_data)
                        field._raw['lookup_values'] = lookup_values
                        field._group_header = group_header
                        fields.append(field)
            
            # Also check if the field_item itself has fieldinfo
            elif 'fieldinfo' in field_item:
                field_data = field_item['fieldinfo'].copy()
                # Handle lookup values separately
                lookup_values = []
                if 'values' in field_data:
                    lookup_values = [
                        {'id': v.get('id'), 'label': v.get('name', '')}
                        for v in field_data['values']
                    ]
                    # Remove from field_data to avoid property setter issue
                    field_data.pop('values', None)
                
                # Create field and add lookup values to raw data
                field = Field(None, field_data)
                field._raw['lookup_values'] = lookup_values
                field._group_header = ''
                fields.append(field)
        
        return fields
    
    @staticmethod
    def filter_excluded_fields(
        fields: List[Field],
        excluded_groups: set = None,
        excluded_labels: set = None,
        excluded_names: set = None
    ) -> List[Field]:
        """Filter out excluded fields.
        
        Args:
            fields: List of fields to filter
            excluded_groups: Set of group headers to exclude
            excluded_labels: Set of labels to exclude
            excluded_names: Set of field names to exclude
            
        Returns:
            Filtered list of fields
        """
        excluded_groups = excluded_groups or set()
        excluded_labels = excluded_labels or set()
        excluded_names = excluded_names or set()
        
        filtered = []
        for field in fields:
            if field.group_header in excluded_groups:
                continue
            if getattr(field, 'label', '') in excluded_labels:
                continue
            if field.name in excluded_names:
                continue
            filtered.append(field)
        
        return filtered