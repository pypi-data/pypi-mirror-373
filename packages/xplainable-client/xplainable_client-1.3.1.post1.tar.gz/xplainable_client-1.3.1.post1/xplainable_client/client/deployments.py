"""
Refactored deployments client using Pydantic models and base client.
"""
from typing import Dict, List, Optional
from uuid import UUID

from .base import BaseClient
from .py_models.deployments import (
    CreateDeploymentRequest,
    CreateDeploymentResponse,
    CreateDeploymentKeyRequest,
    CreateDeploymentKeyResponse,
    DeploymentInfo,
    DeployKeyInfo,
)
from .utils.constants import DEPLOYMENT_ENDPOINTS


class DeploymentsClient(BaseClient):
    """Client for managing model deployments."""
    
    def deploy(self, model_version_id: str) -> CreateDeploymentResponse:
        """
        Deploy a model version.
        
        Args:
            model_version_id: ID of the model version to deploy
            
        Returns:
            CreateDeploymentResponse containing the deployment_id
            
        Raises:
            XplainableAPIError: If deployment fails
        """
        request = CreateDeploymentRequest(model_version_id=model_version_id)
        try:
            return self.post(
                DEPLOYMENT_ENDPOINTS["create"],
                data=request,
                response_model=CreateDeploymentResponse
            )
        except Exception as e:
            # If Pydantic parsing fails, try to handle raw response
            response = self.post(
                DEPLOYMENT_ENDPOINTS["create"],
                data=request
            )
            
            # Try to extract deployment_id from response
            if isinstance(response, dict):
                deployment_id = response.get('deployment_id') or response.get('id') or str(response)
                return CreateDeploymentResponse(deployment_id=deployment_id)
            else:
                # If response is just the ID
                return CreateDeploymentResponse(deployment_id=str(response))
            
            raise
    
    def generate_deploy_key(
        self,
        deployment_id: str,
        description: str = "",
        days_until_expiry: int = 90
    ) -> UUID:
        """
        Generate a deploy key for a deployment.
        
        Args:
            deployment_id: ID of the deployment
            description: Description of the deploy key use case
            days_until_expiry: Number of days until the key expires
            
        Returns:
            The deploy key UUID
            
        Raises:
            XplainableAPIError: If key generation fails
        """
        request = CreateDeploymentKeyRequest(
            deployment_id=deployment_id,
            description=description,
            days_until_expiry=days_until_expiry
        )
        response = self.post(
            DEPLOYMENT_ENDPOINTS["create_deploy_key"],
            data=request,
            response_model=CreateDeploymentKeyResponse
        )
        return response.deploy_key
    
    def list_deployments(self, team_id: Optional[str] = None) -> List[DeploymentInfo]:
        """
        List all deployments for a team.
        
        Args:
            team_id: Optional team ID (uses session team_id if not provided)
            
        Returns:
            List of deployment information
            
        Raises:
            XplainableAPIError: If listing fails
        """
        if not team_id:
            team_id = self.session.team_id
            
        response = self.get(
            DEPLOYMENT_ENDPOINTS["list_team_deployments"],
            team_id=team_id
        )
        
        # Handle different response formats
        if isinstance(response, dict):
            # If response is a dict, try to extract list from various keys
            deployments_data = response.get('deployments', response.get('data', response.get('items', [])))
        elif isinstance(response, list):
            deployments_data = response
        else:
            # If response is something else, try to convert to list
            deployments_data = [response] if response else []
        
        # Parse response into list of DeploymentInfo models
        result = []
        for item in deployments_data:
            try:
                result.append(DeploymentInfo(**item))
            except Exception as e:
                # If Pydantic validation fails, try with raw data
                print(f"Warning: Failed to parse deployment item: {item}, error: {e}")
                continue
                
        return result
    
    def list_deploy_keys(self, deployment_id: str) -> List[DeployKeyInfo]:
        """
        List all deploy keys for a deployment.
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            List of deploy key information
            
        Raises:
            XplainableAPIError: If listing fails
        """
        response = self.get(
            DEPLOYMENT_ENDPOINTS["list_deploy_keys"],
            deployment_id=deployment_id
        )
        
        # Parse response into list of DeployKeyInfo models
        return [DeployKeyInfo(**item) for item in response]
    
    def get_active_team_deploy_keys_count(self, team_id: Optional[str] = None) -> int:
        """
        Get count of active deploy keys for a team.
        
        Args:
            team_id: Optional team ID (uses session team_id if not provided)
            
        Returns:
            Count of active deploy keys
            
        Raises:
            XplainableAPIError: If request fails
        """
        if not team_id:
            team_id = self.session.team_id
            
        return self.get(
            DEPLOYMENT_ENDPOINTS["list_active_team_keys"],
            team_id=team_id
        )
    
    def revoke_deploy_key(self, deployment_id: str, key_id: str) -> Dict[str, str]:
        """
        Revoke a deploy key for a deployment.
        
        Args:
            deployment_id: ID of the deployment
            key_id: ID of the deploy key to revoke
            
        Returns:
            Success message
            
        Raises:
            XplainableAPIError: If revocation fails
        """
        # Note: The API endpoint needs the full request body
        # This might need adjustment based on actual API requirements
        request = {
            "key_id": key_id,
            "deployment_id": deployment_id,
            "organisation_id": self.session.org_id,
            "team_id": self.session.team_id
        }
        
        return self.patch(
            DEPLOYMENT_ENDPOINTS["revoke_key"],
            data=request
        )
    
    def delete_deployment(self, deployment_id: str) -> Dict[str, str]:
        """
        Delete a deployment.
        
        Args:
            deployment_id: ID of the deployment to delete
            
        Returns:
            Success message
            
        Raises:
            XplainableAPIError: If deletion fails
        """
        return self.delete(
            DEPLOYMENT_ENDPOINTS["delete"],
            deployment_id=deployment_id
        )
    
    def activate_deployment(self, deployment_id: str) -> Dict[str, str]:
        """
        Activate a deployment.
        
        Args:
            deployment_id: ID of the deployment to activate
            
        Returns:
            Success message
            
        Raises:
            XplainableAPIError: If activation fails
        """
        return self.patch(
            DEPLOYMENT_ENDPOINTS["activate"],
            data={},  # Empty data for PATCH request
            deployment_id=deployment_id
        )
    
    def get_deployment_payload(self, deployment_id: str) -> List[Dict]:
        """
        Get sample payload data for a deployment.
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            List containing sample data dictionary for inference
            
        Raises:
            XplainableAPIError: If payload generation fails
        """
        return self.get(
            DEPLOYMENT_ENDPOINTS["payload"],
            deployment_id=deployment_id
        )
    
    def deactivate_deployment(self, deployment_id: str) -> Dict[str, str]:
        """
        Deactivate a deployment.
        
        Args:
            deployment_id: ID of the deployment to deactivate
            
        Returns:
            Success message
            
        Raises:
            XplainableAPIError: If deactivation fails
        """
        return self.patch(
            DEPLOYMENT_ENDPOINTS["deactivate"],
            data={},  # Empty data for PATCH request
            deployment_id=deployment_id
        )
    
    # IP Address management methods can be added here when the API endpoints are updated
    # def add_allowed_ip_address(self, deployment_id: str, ip_address: str) -> Dict:
    #     """Add an allowed IP address to a deployment."""
    #     pass
    
    # def list_allowed_ip_addresses(self, deployment_id: str) -> List[str]:
    #     """List allowed IP addresses for a deployment."""
    #     pass