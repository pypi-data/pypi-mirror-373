"""
Metadata Curation Client - API Client

Lightweight API client for external partners to integrate with metadata curation platforms.
Based on the actual models and AbstractExtractor patterns.
"""

import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


class CurationAPIClient:
    """
    API client for external data integration.
    Mirrors the internal ExtractionAPIClient for consistency.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def _handle_response(self, response: requests.Response) -> Dict:
        """Handle API response and raise appropriate exceptions."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"API Error {response.status_code}: {response.text}")
            raise e
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            raise e
    
    # Source endpoints
    def create_source(self, source_data: Dict) -> Dict:
        """Create a new source."""
        response = self.session.post(f"{self.base_url}/sources/", json=source_data)
        return self._handle_response(response)
    
    def get_source(self, source_id: int) -> Dict:
        """Get source by ID."""
        response = self.session.get(f"{self.base_url}/sources/{source_id}")
        return self._handle_response(response)
    
    def get_sources(self) -> List[Dict]:
        """Get all sources."""
        response = self.session.get(f"{self.base_url}/sources/")
        return self._handle_response(response)
    
    def get_source_by_technical_name(self, technical_name: str) -> Optional[Dict]:
        """Get source by technical name."""
        sources = self.get_sources()
        return next((s for s in sources if s.get('technical_name') == technical_name), None)
    
    def get_source_entities(self, source_id: int, include_relationships: bool = False) -> List[Dict]:
        """Get all entities for a source."""
        params = {"include_relationships": include_relationships} if include_relationships else {}
        response = self.session.get(f"{self.base_url}/sources/{source_id}/entities", params=params)
        return self._handle_response(response)
    
    def get_source_properties(self, source_id: int, include_relationships: bool = False) -> List[Dict]:
        """Get all properties for a source."""
        params = {"include_relationships": include_relationships} if include_relationships else {}
        response = self.session.get(f"{self.base_url}/sources/{source_id}/properties", params=params)
        return self._handle_response(response)
    
    def get_source_suggestions(self, source_id: int, include_relationships: bool = False) -> List[Dict]:
        """Get all suggestions for a source."""
        params = {"include_relationships": include_relationships} if include_relationships else {}
        response = self.session.get(f"{self.base_url}/sources/{source_id}/suggestions", params=params)
        return self._handle_response(response)
    
    def update_source(self, source_id: int, source_data: Dict) -> Dict:
        """Update an existing source."""
        response = self.session.put(f"{self.base_url}/sources/{source_id}", json=source_data)
        return self._handle_response(response)
    
    def mark_ingestion_complete(self, source_id: int) -> Dict:
        """Mark ingestion complete by updating last_ingestion_at timestamp."""
        return self.update_source(source_id, {
            "last_ingestion_at": datetime.now().isoformat()
        })
    
    # Entity endpoints
    def create_entity(self, entity_data: Dict) -> Dict:
        """
        Create a new entity.
        
        Required fields:
        - source_id: ID of the source this entity belongs to
        - source_internal_id: Internal ID/identifier for this entity
        
        Optional fields:
        - mapped_from_ids: List of entity IDs this entity is mapped from
        """
        response = self.session.post(f"{self.base_url}/entities/", json=entity_data)
        return self._handle_response(response)
    
    def get_entities(self) -> List[Dict]:
        """Get all entities."""
        response = self.session.get(f"{self.base_url}/entities/")
        return self._handle_response(response)
    
    def get_entity(self, entity_id: int) -> Dict:
        """Get entity by ID."""
        response = self.session.get(f"{self.base_url}/entities/{entity_id}")
        return self._handle_response(response)
    
    # Property endpoints  
    def create_property(self, property_data: Dict) -> Dict:
        """
        Create a new property.
        
        Args:
            property_data: Property data dictionary
        """
        response = self.session.post(f"{self.base_url}/properties/", json=property_data)
        return self._handle_response(response)
    
    def get_properties(self) -> List[Dict]:
        """Get all properties."""
        response = self.session.get(f"{self.base_url}/properties/")
        return self._handle_response(response)
    
    def get_property(self, property_id: int) -> Dict:
        """Get property by ID."""
        response = self.session.get(f"{self.base_url}/properties/{property_id}")
        return self._handle_response(response)
    
    # Suggestion endpoints
    def create_suggestion(self, suggestion_data: Dict) -> Dict:
        """
        Create a new suggestion.
        
        Required fields:
        - source_id: ID of the source
        - entity_id: ID of the entity
        - property_id: ID of the property
        
        For multiple_choice properties:
        - property_option_id: ID of the property option
        
        For free_text, numerical, or other properties:
        - custom_value: String value for the property
        
        Note: Either property_option_id OR custom_value must be provided,
        depending on the property type.
        """
        response = self.session.post(f"{self.base_url}/suggestions/", json=suggestion_data)
        return self._handle_response(response)
    
    def get_suggestions(self) -> List[Dict]:
        """Get all suggestions."""
        response = self.session.get(f"{self.base_url}/suggestions/")
        return self._handle_response(response)


# Property type constants (matching models.py)
class PropertyType:
    """
    Property type constants for creating properties.

    MULTIPLE_CHOICE: Property with predefined options
        - Requires property_options list when creating
        - Suggestions require property_option_id

    SINGLE_CHOICE: Property with predefined options (single selection)
        - Requires property_options list when creating
        - Suggestions require property_option_id

    FREE_TEXT: Property with open text values
        - No property_options needed
        - Suggestions require custom_value (string)

    BINARY: Boolean/yes-no property
        - Automatically creates "1" and "0" options
        - Suggestions require property_option_id (use option with name "1" for true)

    NUMERICAL: Numeric property
        - No property_options needed
        - Suggestions require custom_value (numeric value as string)
    """
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    FREE_TEXT = "free_text"
    BINARY = "binary"
    NUMERICAL = "numerical"
