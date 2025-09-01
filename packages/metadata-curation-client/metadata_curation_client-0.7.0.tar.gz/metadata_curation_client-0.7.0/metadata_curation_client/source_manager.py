"""
Metadata Curation Client - Source Manager

Enhanced abstractions for the metadata curation API client, inspired by the internal AbstractExtractor.

This provides higher-level functionality for external integrators who prefer a more
streamlined approach with features like:
- Pre-fetching data to reduce API calls
- Lookup tables for efficient access
- Automatic property creation and validation
- Streamlined suggestion creation
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from .curation_api_client import CurationAPIClient, PropertyType


class SourceManager:
    """
    High-level manager for source data integration.
    
    Provides similar convenience features to the internal AbstractExtractor:
    - Prefetches data to reduce API calls
    - Maintains lookup tables for entities, properties, and suggestions
    - Automatically creates global properties from definitions
    - Handles validation for different property types
    - Deduplicates suggestions
    
    This is optional - partners can still use the direct CurationAPIClient
    for simpler integrations if preferred.
    """
    
    def __init__(self, client: CurationAPIClient, source_identifier: Union[int, str], property_definitions: Optional[List[Dict]] = None):
        """
        Initialize the source manager with all needed data.
        
        Args:
            client: API client for backend communication
            source_identifier: Source ID (int) or technical_name (str)
            property_definitions: Optional list of property definitions to ensure exist
        """
        self.client = client
        self.property_definitions = property_definitions or []
        
        # Step 1: Get source information
        self.source = self._get_or_create_source(source_identifier)
        self.source_id = self.source['id']
        
        print(f"🎯 Working with source: {self.source['name']} (ID: {self.source_id})")
        
        # Step 2: Fetch all current data via API
        self._fetch_all_data()
        
        # Step 3: Build lookup dictionaries
        self._build_lookups()
        
        # Step 4: Ensure required properties exist (global properties now)
        if self.property_definitions:
            self._ensure_properties_exist()
    
    def _get_or_create_source(self, source_identifier: Union[int, str]) -> Dict:
        """Get source by ID or technical name. If not found by technical name, create a new source."""
        if isinstance(source_identifier, int) or (isinstance(source_identifier, str) and source_identifier.isdigit()):
            source_id = int(source_identifier)
            return self.client.get_source(source_id)
        else:
            # Get all sources and filter by technical_name
            response = self.client.get_sources()
            source = next((s for s in response if s.get('technical_name') == source_identifier), None)
            if not source:
                print(f"⚠️  Source '{source_identifier}' not found. Creating new source...")
                # Create a new source with the given technical_name and a default name/description
                source_data = {
                    'name': source_identifier.replace('_', ' ').title(),
                    'description': f"Auto-created source for '{source_identifier}'",
                    'technical_name': source_identifier
                }
                source = self.client.create_source(source_data)
            return source
    
    def _fetch_all_data(self):
        """Fetch all information via API to reduce individual calls later."""
        print("📡 Fetching all data from API...")
        
        # Get all source-related data
        self.entities = self.client.get_source_entities(self.source_id)
        self.properties = self.client.get_properties()
        self.suggestions = self.client.get_source_suggestions(self.source_id)
        
        print(f"   📚 {len(self.entities)} entities")
        print(f"   🏷️  {len(self.properties)} global properties")  
        print(f"   💡 {len(self.suggestions)} suggestions")
    
    def _build_lookups(self):
        """Build lookup dictionaries for efficient access."""
        print("🔍 Building lookup dictionaries...")
        
        # Entities by internal ID
        self.entities_by_internal_id = {
            entity['source_internal_id']: entity 
            for entity in self.entities
        }
        
        # Properties by technical name
        self.properties_by_tech_name = {
            prop['technical_name']: prop 
            for prop in self.properties
        }
        
        # Suggestions by entity and property
        self.suggestions_lookup = {}
        for suggestion in self.suggestions:
            key = (suggestion['entity_id'], suggestion['property_id'])
            if key not in self.suggestions_lookup:
                self.suggestions_lookup[key] = []
            self.suggestions_lookup[key].append(suggestion)
    
    def get_or_create_entity(self, internal_id: str) -> Dict:
        """Get existing entity or create new one."""
        if internal_id in self.entities_by_internal_id:
            return self.entities_by_internal_id[internal_id]
        
        # Create new entity
        entity_data = {
            'source_id': self.source_id,
            'source_internal_id': internal_id,
            'mapped_from_ids': []
        }
        
        entity = self.client.create_entity(entity_data)
        self.entities_by_internal_id[internal_id] = entity
        self.entities.append(entity)
        
        print(f"   ➕ Created entity: {internal_id}")
        return entity
    
    def create_suggestion(self, entity_id: int, property_name: str, value: Any) -> Optional[Dict]:
        """
        Create a single property suggestion with validation and deduplication.
        
        Args:
            entity_id: ID of the entity
            property_name: Technical name of the property
            value: Value to suggest (will be validated based on property type)
        
        Returns:
            Created suggestion or None if invalid/skipped
        """
        # Skip empty or None values
        if value is None or value == "":
            return None
        
        # Find the property object
        property_obj = self.properties_by_tech_name.get(property_name)
        if not property_obj:
            print(f"   ⚠️  Property '{property_name}' not found")
            return None
        
        property_id = property_obj['id']
        property_type = property_obj['type']
        suggestion_key = (entity_id, property_id)
        
        # Check if suggestion with same value already exists
        if self._suggestion_exists(suggestion_key, value, property_obj):
            print(f"   ⏭️  Skipping duplicate suggestion: {property_name} = '{value}'")
            return None
        
        # Prepare suggestion data based on property type
        suggestion_data = {
            'entity_id': entity_id,
            'property_id': property_id,
            'source_id': self.source_id,
        }
        
        if property_type in [PropertyType.MULTIPLE_CHOICE, PropertyType.SINGLE_CHOICE, PropertyType.BINARY]:
            # Find matching option
            property_options = property_obj.get('property_options', [])
            str_value = str(value).strip()
            
            if property_type == PropertyType.BINARY:
                # Normalize binary values (1/0, true/false, yes/no)
                if str_value.lower() in ['1', 'true', 'yes', 'y']:
                    option_name = '1'
                elif str_value.lower() in ['0', 'false', 'no', 'n']:
                    option_name = '0'
                else:
                    print(f"   ⚠️  Invalid binary value: '{value}'")
                    return None
            else:
                option_name = str_value
            
            # Find matching option
            matching_option = next(
                (opt for opt in property_options if opt['name'].lower() == option_name.lower()),
                None
            )
            
            if not matching_option:
                print(f"   ⚠️  No matching option for '{str_value}'")
                return None
            
            suggestion_data['property_option_id'] = matching_option['id']
            
        elif property_type in [PropertyType.FREE_TEXT, PropertyType.NUMERICAL]:
            # For numerical values, validate it's a number
            if property_type == PropertyType.NUMERICAL:
                try:
                    float(str(value))  # Check if it's a valid number
                except ValueError:
                    print(f"   ⚠️  Invalid numerical value: '{value}'")
                    return None
            
            # Use custom value for free text and numerical properties
            suggestion_data['custom_value'] = str(value)
            
        else:
            print(f"   ⚠️  Unknown property type: {property_type}")
            return None
        
        # Create the suggestion
        try:
            suggestion = self.client.create_suggestion(suggestion_data)
            
            # Add to our lookup for future reference
            if suggestion_key not in self.suggestions_lookup:
                self.suggestions_lookup[suggestion_key] = []
            self.suggestions_lookup[suggestion_key].append(suggestion)
            self.suggestions.append(suggestion)
            
            print(f"   💡 Created suggestion: {property_name} = '{value}'")
            return suggestion
            
        except Exception as e:
            print(f"   ⚠️  Failed to create suggestion: {e}")
            return None
    
    def _suggestion_exists(self, suggestion_key: tuple, new_value: Any, property_obj: Dict) -> bool:
        """Check if a suggestion with the same value already exists."""
        existing_suggestions = self.suggestions_lookup.get(suggestion_key, [])
        if not existing_suggestions:
            return False
        
        property_type = property_obj.get('type')
        str_value = str(new_value).strip()
        
        for suggestion in existing_suggestions:
            if property_type in [PropertyType.MULTIPLE_CHOICE, PropertyType.SINGLE_CHOICE, PropertyType.BINARY]:
                # Get the option that matches new_value
                if property_type == PropertyType.BINARY:
                    # Normalize binary values
                    if str_value.lower() in ['1', 'true', 'yes', 'y']:
                        normalized_value = '1'
                    elif str_value.lower() in ['0', 'false', 'no', 'n']:
                        normalized_value = '0'
                    else:
                        continue  # Invalid binary value
                else:
                    normalized_value = str_value
                
                # Check if option ID matches
                property_options = property_obj.get('property_options', [])
                for option in property_options:
                    if option['name'].lower() == normalized_value.lower():
                        if suggestion.get('property_option_id') == option['id']:
                            return True
            
            elif property_type in [PropertyType.FREE_TEXT, PropertyType.NUMERICAL]:
                # For free text and numerical, compare custom_value
                if suggestion.get('custom_value', '').strip() == str_value:
                    return True
        
        return False
    
    def create_suggestions_batch(self, entity_id: int, data: Dict[str, Any]) -> Dict:
        """
        Create multiple suggestions in a batch.
        
        Args:
            entity_id: ID of the entity
            data: Dictionary mapping property technical names to values
        
        Returns:
            Dictionary with counts of created and skipped suggestions
        """
        created_count = 0
        skipped_count = 0
        
        for property_name, value in data.items():
            # Handle both single values and lists of values
            values_to_process = value if isinstance(value, list) else [value]
            
            for individual_value in values_to_process:
                # Skip empty or None list items
                if individual_value is None or individual_value == "":
                    continue
                
                suggestion = self.create_suggestion(entity_id, property_name, individual_value)
                if suggestion:
                    created_count += 1
                else:
                    skipped_count += 1
        
        if created_count > 0 or skipped_count > 0:
            print(f"   ✅ Suggestions: {created_count} created, {skipped_count} skipped")
        
        return {
            'created': created_count,
            'skipped': skipped_count
        }
    
    def finish_ingestion(self):
        """Mark ingestion complete by updating the timestamp."""
        try:
            update_data = {
                'last_ingestion_at': datetime.now().isoformat()
            }
            updated_source = self.client.update_source(self.source_id, update_data)
            print(f"📅 Updated last ingestion timestamp for: {self.source['name']}")
            return updated_source
        except Exception as e:
            print(f"⚠️  Failed to update last ingestion timestamp: {e}")
            return None
    
    def _ensure_properties_exist(self):
        """Create any properties that don't exist yet (properties are now global)."""
        print("🏷️  Ensuring properties exist...")
        
        created_count = 0
        for prop_def in self.property_definitions:
            tech_name = prop_def['technical_name']
            
            if tech_name not in self.properties_by_tech_name:
                # Create the property (no source_id needed anymore)
                property_data = {
                    'technical_name': tech_name,
                    'name': prop_def['name'],
                    'type': prop_def['type'],
                    'property_options': []
                }
                
                # Add description if provided
                if 'description' in prop_def and prop_def['description']:
                    property_data['description'] = prop_def['description']
                
                # Add options for controlled vocabulary and binary
                if prop_def['type'] in [PropertyType.MULTIPLE_CHOICE, PropertyType.SINGLE_CHOICE] and 'options' in prop_def:
                    property_data['property_options'] = [
                        {'name': option} for option in prop_def['options']
                    ]
                elif prop_def['type'] == PropertyType.BINARY:
                    property_data['property_options'] = [
                        {'name': '0'}, {'name': '1'}
                    ]
                
                # Create via API with source_id for automatic prefixing
                created_property = self.client.create_property(property_data)
                self.properties_by_tech_name[tech_name] = created_property
                self.properties.append(created_property)
                created_count += 1
                
                print(f"   ➕ Created: {prop_def['name']} ({prop_def['type']})")
        
        if created_count == 0:
            print(f"   ✅ All {len(self.property_definitions)} properties already exist")
        else:
            print(f"   ✅ Created {created_count} new properties")

class PropertyBuilder:
    """Helper class to build property definitions with proper validation."""
    
    @staticmethod
    def free_text(technical_name: str, display_name: str, description: str = "") -> Dict:
        """Create a free text property definition."""
        return {
            'technical_name': technical_name,
            'name': display_name,
            'description': description,
            'type': PropertyType.FREE_TEXT
        }
    
    @staticmethod
    def multiple_choice(technical_name: str, display_name: str, options: List[str], description: str = "") -> Dict:
        """Create a multiple choice property definition."""
        return {
            'technical_name': technical_name,
            'name': display_name,
            'type': PropertyType.MULTIPLE_CHOICE,
            'options': options,
            'description': description,
        }

    @staticmethod
    def single_choice(technical_name: str, display_name: str, options: List[str], description: str = "") -> Dict:
        """Create a single choice property definition."""
        return {
            'technical_name': technical_name,
            'name': display_name,
            'type': PropertyType.SINGLE_CHOICE,
            'options': options,
            'description': description,
        }
    
    @staticmethod
    def binary(technical_name: str, display_name: str, description: str = "") -> Dict:
        """Create a binary property definition."""
        return {
            'technical_name': technical_name,
            'name': display_name,
            'description': description,
            'type': PropertyType.BINARY
        }
    
    @staticmethod
    def numerical(technical_name: str, display_name: str, description: str = "") -> Dict:
        """Create a numerical property definition."""
        return {
            'technical_name': technical_name,
            'name': display_name,
            'description': description,
            'type': PropertyType.NUMERICAL
        }


class SourceBuilder:
    """Helper class to create a new source."""
    
    @staticmethod
    def create(client: CurationAPIClient, name: str, description: str, technical_name: str = None) -> Dict:
        """
        Create a new source with the given parameters.
        
        Args:
            client: The API client to use
            name: Display name for the source
            description: Description of the source
            technical_name: Optional technical name (slug)
            
        Returns:
            The created source
        """
        source_data = {
            'name': name,
            'description': description
        }
        
        if technical_name:
            source_data['technical_name'] = technical_name
            
        return client.create_source(source_data)


class EntityBuilder:
    """Helper class to create entities."""
    
    @staticmethod
    def create(client: CurationAPIClient, source_id: int, internal_id: str) -> Dict:
        """
        Create a new entity for a source.
        
        Args:
            client: The API client to use
            source_id: ID of the source
            internal_id: Internal ID/identifier for this entity
            
        Returns:
            The created entity
        """
        entity_data = {
            'source_id': source_id,
            'source_internal_id': internal_id,
            'mapped_from_ids': []
        }
        
        return client.create_entity(entity_data)
