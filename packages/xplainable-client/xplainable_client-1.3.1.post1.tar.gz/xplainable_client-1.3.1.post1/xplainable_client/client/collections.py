"""
Refactored collections client using Pydantic models and base client.
"""
from typing import Dict, List, Optional

from .base import BaseClient
from .py_models.collections import (
    CreateCollectionRequest,
    CreateCollectionResponse,
    UpdateCollectionNameRequest,
    UpdateCollectionDescriptionRequest,
    CollectionInfo,
    CreateScenariosRequest,
    ScenarioInfo,
)
from .utils.constants import COLLECTION_ENDPOINTS


class CollectionsClient(BaseClient):
    """Client for managing model collections."""
    
    def create_collection(
        self,
        model_id: str,
        name: str,
        description: str
    ) -> str:
        """
        Create a new collection for a model.
        
        Args:
            model_id: ID of the model
            name: Name of the collection
            description: Description of the collection
            
        Returns:
            The collection ID
            
        Raises:
            XplainableAPIError: If collection creation fails
        """
        request = CreateCollectionRequest(
            model_id=model_id,
            name=name, 
            description=description
        )
        
        response = self.post(
            COLLECTION_ENDPOINTS["create"],
            data=request,
            response_model=CreateCollectionResponse
        )
        
        return response
    
    def get_model_collections(self, model_id: str) -> List[CollectionInfo]:
        """
        Get all collections for a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            List of collection information
            
        Raises:
            XplainableAPIError: If retrieval fails
        """
        response = self.get(
            COLLECTION_ENDPOINTS["get_model_collections"],
            model_id=model_id,
            ext=self.session._ext if hasattr(self.session, '_ext') else 'client'
        )
        
        # Parse response into list of CollectionInfo models
        if isinstance(response, list):
            return [CollectionInfo(**item) for item in response]
        return []
    
    def get_team_collections(self) -> List[dict]:
        """
        Get all collections for the team.
        
        Returns:
            List of collection information
            
        Raises:
            XplainableAPIError: If retrieval fails
        """
        return self.get(COLLECTION_ENDPOINTS["get_team_collections"])
    
    def update_collection_name(
        self,
        model_id: str,
        collection_id: str,
        name: str
    ) -> Dict[str, str]:
        """
        Update the name of a collection.
        
        Args:
            model_id: ID of the model
            collection_id: ID of the collection
            name: New name for the collection
            
        Returns:
            Success message
            
        Raises:
            XplainableAPIError: If update fails
        """
        request = UpdateCollectionNameRequest(name=name)
        
        return self.patch(
            COLLECTION_ENDPOINTS["update_name"],
            data=request,
            model_id=model_id,
            collection_id=collection_id,
            ext=self.session._ext if hasattr(self.session, '_ext') else 'client'
        )
    
    def update_collection_description(
        self,
        model_id: str,
        collection_id: str,
        description: str
    ) -> Dict[str, str]:
        """
        Update the description of a collection.
        
        Args:
            model_id: ID of the model
            collection_id: ID of the collection
            description: New description for the collection
            
        Returns:
            Success message
            
        Raises:
            XplainableAPIError: If update fails
        """
        request = UpdateCollectionDescriptionRequest(description=description)
        
        return self.patch(
            COLLECTION_ENDPOINTS["update_description"],
            data=request,
            model_id=model_id,
            collection_id=collection_id,
            ext=self.session._ext if hasattr(self.session, '_ext') else 'client'
        )
    
    def delete_collection(
        self,
        model_id: str,
        collection_id: str
    ) -> Dict[str, str]:
        """
        Delete a collection.
        
        Args:
            model_id: ID of the model
            collection_id: ID of the collection to delete
            
        Returns:
            Success message
            
        Raises:
            XplainableAPIError: If deletion fails
        """
        return self.delete(
            COLLECTION_ENDPOINTS["delete"],
            collection_id=collection_id
        )
    
    def create_scenarios(
        self,
        collection_id: str,
        scenarios: list[dict]
    ) -> List[dict]:
        """
        Create scenarios for a collection.
        
        Args:
            collection_id: ID of the collection
            scenarios: List of scenario data
            
        Returns:
            List of created scenarios
            
        Raises:
            XplainableAPIError: If creation fails
        """
        request = CreateScenariosRequest(scenarios=scenarios)
        
        return self.post(
            COLLECTION_ENDPOINTS["create_scenarios"],
            data=request,
            collection_id=collection_id
        )
    
    def get_collection_scenarios(self, collection_id: str) -> List[dict]:
        """
        Get all scenarios for a collection.
        
        Args:
            collection_id: ID of the collection
            
        Returns:
            List of scenarios
            
        Raises:
            XplainableAPIError: If retrieval fails
        """
        return self.get(
            COLLECTION_ENDPOINTS["get_scenarios"],
            collection_id=collection_id
        )