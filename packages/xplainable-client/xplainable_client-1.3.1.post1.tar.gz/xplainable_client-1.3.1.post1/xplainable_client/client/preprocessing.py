"""
Simplified preprocessing client - business logic moved to API.
"""
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import json
import pickle
import base64
from xplainable.preprocessing.pipeline import XPipeline

from .base import BaseClient, XplainableAPIError
from .py_models.preprocessing import (
    CreatePreprocessorResponse,
    AddPreprocessorVersionResponse, 
    UpdatePreprocessorVersionResponse,
    PreprocessorInfo,
)
from .utils.constants import PREPROCESSOR_ENDPOINTS


class PreprocessingClient(BaseClient):
    """Client for managing data preprocessing pipelines."""
    
    def create_preprocessor(
        self,
        preprocessor_name: str,
        preprocessor_description: str,
        pipeline: XPipeline,
        df: pd.DataFrame
    ) -> Tuple[str, str]:
        """
        Create a new preprocessor - sends pipeline object to API for processing.
        
        Args:
            preprocessor_name: Name of the preprocessor
            preprocessor_description: Description of the preprocessor
            pipeline: The preprocessing pipeline
            df: Sample dataframe for the pipeline
            
        Returns:
            Tuple of (preprocessor_id, version_id)
            
        Raises:
            XplainableAPIError: If preprocessor creation fails
            ValueError: If a preprocessor with the same name already exists
        """
        if df is None:
            raise ValueError("No dataframe provided.")
        
        # Serialize pipeline and dataframe for sending to API
        pipeline_serialized = base64.b64encode(pickle.dumps(pipeline)).decode('utf-8')
        df_json = df.to_json(orient='records')
        
        # Create simple request - API handles all business logic
        request_data = {
            "preprocessor_name": preprocessor_name,
            "preprocessor_description": preprocessor_description,
            "pipeline_serialized": pipeline_serialized,
            "df_json": df_json,
            "python_version": self.session.python_version,
            "xplainable_version": self.session.xplainable_version
        }
        
        try:
            response = self.post(
                PREPROCESSOR_ENDPOINTS["create_from_pipeline"],
                data=request_data,
                response_model=CreatePreprocessorResponse
            )
            return response.preprocessor_id, response.version_id
        except XplainableAPIError as e:
            if e.status_code == 409:
                raise ValueError(f"A preprocessor with the name '{preprocessor_name}' already exists.")
            raise
    
    def add_version(
        self,
        preprocessor_id: str,
        pipeline: XPipeline,
        df: pd.DataFrame
    ) -> str:
        """
        Add a new version to an existing preprocessor.
        
        Args:
            preprocessor_id: ID of the existing preprocessor
            pipeline: The preprocessing pipeline
            df: Sample dataframe for the pipeline
            
        Returns:
            The new version_id
            
        Raises:
            XplainableAPIError: If version addition fails
        """
        if df is None:
            raise ValueError("No dataframe provided.")
        
        # Serialize pipeline and dataframe for sending to API
        pipeline_serialized = base64.b64encode(pickle.dumps(pipeline)).decode('utf-8')
        df_json = df.to_json(orient='records')
        
        request_data = {
            "preprocessor_id": preprocessor_id,
            "pipeline_serialized": pipeline_serialized,
            "df_json": df_json,
            "python_version": self.session.python_version,
            "xplainable_version": self.session.xplainable_version
        }
        
        response = self.post(
            PREPROCESSOR_ENDPOINTS["add_version_from_pipeline"],
            data=request_data,
            response_model=AddPreprocessorVersionResponse
        )
        return response.version_id
    
    def update_version_from_pipeline(
        self,
        version_id: str,
        pipeline: XPipeline,
        df: pd.DataFrame
    ) -> str:
        """
        Update an existing preprocessor version with complete pipeline.
        
        Args:
            version_id: ID of the version to update
            pipeline: The complete preprocessing pipeline (existing + new stages)
            df: Sample dataframe for the pipeline
            
        Returns:
            The updated version_id
            
        Raises:
            XplainableAPIError: If version update fails
        """
        if df is None:
            raise ValueError("No dataframe provided.")
        
        # Serialize pipeline and dataframe for sending to API
        pipeline_serialized = base64.b64encode(pickle.dumps(pipeline)).decode('utf-8')
        df_json = df.to_json(orient='records')
        
        request_data = {
            "version_id": version_id,
            "pipeline_serialized": pipeline_serialized,
            "df_json": df_json
        }
        
        response = self.post(
            PREPROCESSOR_ENDPOINTS["update_version_from_pipeline"],
            data=request_data,
            response_model=UpdatePreprocessorVersionResponse
        )
        return response.version_id
    
    def load_preprocessor(
        self,
        version_id: str,
        preprocessor_id: Optional[str] = None,
        response_only: bool = False
    ):
        """
        Load a preprocessor by version_id - API handles reconstruction.
        
        Args:
            version_id: The version ID of the preprocessor
            preprocessor_id: Optional preprocessor ID (will be resolved from version_id if not provided)
            response_only: If True, returns only the metadata
            
        Returns:
            The loaded pipeline or metadata
            
        Raises:
            XplainableAPIError: If loading fails
        """
        if response_only:
            # Get metadata only
            response = self.get(
                PREPROCESSOR_ENDPOINTS["get_version"],
                version_id=version_id
            )
            return response
        
        # Request reconstructed pipeline from API
        response = self.get(
            PREPROCESSOR_ENDPOINTS["load_pipeline"],
            version_id=version_id
        )
        
        # Deserialize the pipeline sent back from API
        if "pipeline_serialized" in response:
            pipeline_bytes = base64.b64decode(response["pipeline_serialized"].encode('utf-8'))
            return pickle.loads(pipeline_bytes)
        
        # Fallback: let API handle reconstruction and send back serialized pipeline
        return response
    
    def list_preprocessors(self, team_id: Optional[str] = None) -> List[PreprocessorInfo]:
        """
        List all preprocessors for a team.
        
        Args:
            team_id: Optional team ID (uses session team_id if not provided)
            
        Returns:
            List of preprocessor information
            
        Raises:
            XplainableAPIError: If listing fails
        """
        if not team_id:
            team_id = self.session.team_id
        
        response = self.get(
            PREPROCESSOR_ENDPOINTS["list_team_preprocessors"],
            params={"team_id": team_id}
        )
        
        # Parse response into list of PreprocessorInfo models
        return [PreprocessorInfo(**item) for item in response]
    
    def get_preprocessor(self, preprocessor_id: str) -> PreprocessorInfo:
        """
        Get detailed information about a preprocessor.
        
        Args:
            preprocessor_id: ID of the preprocessor
            
        Returns:
            Preprocessor information
            
        Raises:
            XplainableAPIError: If retrieval fails
        """
        return self.get(
            PREPROCESSOR_ENDPOINTS["get"],
            response_model=PreprocessorInfo,
            preprocessor_id=preprocessor_id
        )
    
    def apply_preprocessor(
        self,
        version_id: str,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Apply a preprocessor version to a dataframe.
        
        Args:
            version_id: ID of the preprocessor version
            df: Dataframe to transform
            
        Returns:
            Transformed dataframe
            
        Raises:
            XplainableAPIError: If application fails
        """
        # Convert dataframe to JSON for sending
        df_json = df.to_json(orient='records')
        
        response = self.post(
            PREPROCESSOR_ENDPOINTS["apply"],
            data={
                "version_id": version_id,
                "data": df_json
            }
        )
        
        # Convert response back to dataframe
        return pd.DataFrame(response)
    
    def update_version_from_stages(
        self,
        version_id: str,
        stages: list,
        deltas: list
    ) -> str:
        """
        Update a preprocessor version from pre-computed stages and deltas (bypasses pipeline serialization).
        This is useful for autotrain service with dynamically created classes that can't be pickled.
        
        Args:
            version_id: ID of the version to update
            stages: Pre-computed stages list
            deltas: Pre-computed deltas list
            
        Returns:
            The updated version_id
        """
        # Use the original update endpoint with stages/deltas
        request_data = {
            "version_id": version_id,
            "stages": stages,
            "deltas": deltas,
            "versions": {}  # Empty for update operations
        }
        
        try:
            response = self.post(
                PREPROCESSOR_ENDPOINTS["update_version"],
                data=request_data,
                response_model=UpdatePreprocessorVersionResponse
            )
            return response.version_id
        except XplainableAPIError as e:
            raise
    
    def create_preprocessor_from_stages(
        self,
        preprocessor_name: str,
        preprocessor_description: str,
        stages: list,
        deltas: list,
        versions: dict
    ) -> Tuple[str, str]:
        """
        Create preprocessor from pre-computed stages and deltas (bypasses pipeline serialization).
        This is useful for autotrain service with dynamically created classes that can't be pickled.
        
        Args:
            preprocessor_name: Name of the preprocessor
            preprocessor_description: Description of the preprocessor
            stages: Pre-computed stages list
            deltas: Pre-computed deltas list
            versions: Version information dict
            
        Returns:
            Tuple of (preprocessor_id, version_id)
        """
        # Use the original create endpoint with stages/deltas
        request_data = {
            "preprocessor_name": preprocessor_name,
            "preprocessor_description": preprocessor_description,
            "stages": stages,
            "deltas": deltas,
            "versions": versions
        }
        
        try:
            response = self.post(
                PREPROCESSOR_ENDPOINTS["create"],
                data=request_data,
                response_model=CreatePreprocessorResponse
            )
            return response.preprocessor_id, response.version_id
        except XplainableAPIError as e:
            if e.status_code == 409:
                raise ValueError(f"A preprocessor with the name '{preprocessor_name}' already exists.")
            raise