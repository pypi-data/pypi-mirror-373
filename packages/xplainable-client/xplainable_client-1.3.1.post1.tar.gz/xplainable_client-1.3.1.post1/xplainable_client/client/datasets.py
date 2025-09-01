"""
Refactored datasets client using Pydantic models and base client.
"""
from typing import Dict, List, Optional
import pandas as pd

from .base import BaseClient, XplainableAPIError
from .py_models.datasets import (
    DatasetInfo,
    DatasetListResponse,
    DatasetUploadRequest,
    DatasetUploadResponse,
)


class DatasetsClient(BaseClient):
    """Client for managing datasets."""
    
    # Base URL for public datasets storage
    DATASET_BASE_URL = "https://xplainablepublic.blob.core.windows.net/asset-repository/datasets"
    
    def list_datasets(self) -> List[str]:
        """
        List all available public datasets.
        
        Returns:
            List of dataset names
            
        Raises:
            XplainableAPIError: If listing fails
        """
        # This endpoint doesn't use the session, it's a public endpoint
        import requests
        
        try:
            response = requests.get('https://platform.xplainable.io/v1/public-datasets')
            
            if response.status_code != 200:
                raise XplainableAPIError(
                    status_code=response.status_code,
                    message="Unable to list datasets. Check your connection and try again."
                )
            
            return response.json()
            
        except requests.RequestException as e:
            raise XplainableAPIError(
                status_code=0,
                message=f"Network error while listing datasets: {str(e)}"
            )
    
    def load_dataset(self, name: str) -> pd.DataFrame:
        """
        Load a public dataset by name.
        
        Args:
            name: Name of the dataset to load
            
        Returns:
            DataFrame containing the dataset
            
        Raises:
            ValueError: If dataset doesn't exist
            XplainableAPIError: If loading fails
        """
        # List available datasets to validate
        available_datasets = self.list_datasets()
        
        if name not in available_datasets:
            raise ValueError(
                f"'{name}' is not available. "
                f"Available datasets: {', '.join(available_datasets)}"
            )
        
        try:
            # Construct URL for the dataset
            url = self._get_dataset_url(name)
            
            # Load the dataset
            df = pd.read_csv(url)
            return df
            
        except Exception as e:
            raise XplainableAPIError(
                status_code=0,
                message=f"Unable to load dataset '{name}': {str(e)}"
            )
    
    def _get_dataset_url(self, name: str) -> str:
        """
        Get the URL for a dataset.
        
        Args:
            name: Name of the dataset
            
        Returns:
            Full URL to the dataset CSV file
        """
        return f"{self.DATASET_BASE_URL}/{name}/data.csv"
    
    def upload_dataset(
        self,
        file_path: str,
        name: str,
        description: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> DatasetUploadResponse:
        """
        Upload a dataset file.
        
        Args:
            file_path: Path to the dataset file
            name: Name for the dataset
            description: Optional description
            team_id: Optional team ID (uses session team_id if not provided)
            
        Returns:
            Upload response with dataset information
            
        Raises:
            FileNotFoundError: If file doesn't exist
            XplainableAPIError: If upload fails
        """
        if not team_id:
            team_id = self.session.team_id
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {
                    'name': name,
                    'description': description,
                    'team_id': team_id
                }
                
                # Note: This endpoint would need to be added to the API
                url = f"{self.session.hostname}/v1/client/datasets/upload"
                response = self.session._session.post(
                    url=url,
                    files=files,
                    data=data
                )
                
                result = self._handle_response(response, DatasetUploadResponse)
                return result
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        except Exception as e:
            raise XplainableAPIError(
                status_code=0,
                message=f"Failed to upload dataset: {str(e)}"
            )
    
    def delete_dataset(self, dataset_id: str) -> Dict[str, str]:
        """
        Delete a dataset.
        
        Args:
            dataset_id: ID of the dataset to delete
            
        Returns:
            Success message
            
        Raises:
            XplainableAPIError: If deletion fails
        """
        # Note: This endpoint would need to be added to the API
        url = f"{self.session.hostname}/v1/client/datasets/{dataset_id}"
        response = self.session._session.delete(url=url)
        
        return self._handle_response(response)
    
    def get_dataset_info(self, dataset_id: str) -> DatasetInfo:
        """
        Get information about a specific dataset.
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            Dataset information
            
        Raises:
            XplainableAPIError: If retrieval fails
        """
        # Note: This endpoint would need to be added to the API
        url = f"{self.session.hostname}/v1/client/datasets/{dataset_id}"
        response = self.session._session.get(url=url)
        
        return self._handle_response(response, DatasetInfo)
    
    def preview_dataset(
        self,
        dataset_id: str,
        rows: int = 10
    ) -> pd.DataFrame:
        """
        Preview a dataset by returning first N rows.
        
        Args:
            dataset_id: ID of the dataset
            rows: Number of rows to preview
            
        Returns:
            DataFrame with preview data
            
        Raises:
            XplainableAPIError: If preview fails
        """
        # Note: This endpoint would need to be added to the API
        url = f"{self.session.hostname}/v1/client/datasets/{dataset_id}/preview"
        response = self.session._session.get(
            url=url,
            params={'rows': rows}
        )
        
        result = self._handle_response(response)
        return pd.DataFrame(result)
    
    def list_team_datasets(self, team_id: Optional[str] = None) -> List[DatasetInfo]:
        """
        List all datasets for a team.
        
        Args:
            team_id: Optional team ID (uses session team_id if not provided)
            
        Returns:
            List of dataset information
            
        Raises:
            XplainableAPIError: If listing fails
        """
        if not team_id:
            team_id = self.session.team_id
        
        # Note: This endpoint would need to be added to the API
        url = f"{self.session.hostname}/v1/client/datasets/teams/{team_id}"
        response = self.session._session.get(url=url)
        
        result = self._handle_response(response)
        if isinstance(result, list):
            return [DatasetInfo(**item) for item in result]
        return []