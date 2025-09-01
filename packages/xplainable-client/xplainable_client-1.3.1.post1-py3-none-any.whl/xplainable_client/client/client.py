"""
Refactored main Xplainable client that integrates all service clients.
"""
from typing import Optional

from .session import Session
from .deployments import DeploymentsClient
from .preprocessing import PreprocessingClient
from .collections import CollectionsClient
from .datasets import DatasetsClient
from .inference import InferenceClient
from .gpt import GPTClient
from .autotrain import AutotrainClient
from .misc import MiscClient

# Import ModelsClient directly from models.py file (not models/ directory)
from .models import ModelsClient


class XplainableClient:
    """
    Main client for interacting with the Xplainable API.
    
    This client provides a unified interface to all Xplainable services
    using type-safe Pydantic models and consistent error handling.
    
    Example:
        >>> client = XplainableClient(api_key="your-api-key")
        >>> models = client.models.list_team_models()
        >>> deployment = client.deployments.deploy(model_version_id="...")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        hostname: str = 'https://platform.xplainable.io',
        org_id: Optional[str] = None,
        team_id: Optional[str] = None
    ):
        """
        Initialize the Xplainable client.
        
        Args:
            api_key: Your Xplainable API key (required)
            hostname: The API hostname (defaults to production)
            org_id: Optional organization ID
            team_id: Optional team ID
            
        Raises:
            ValueError: If api_key is not provided
            XplainableAPIError: If authentication fails
        """
        # Initialize session for authentication and HTTP handling
        self.session = Session(
            api_key=api_key,
            hostname=hostname,
            org_id=org_id,
            team_id=team_id
        )
        
        # Initialize service clients
        self._init_service_clients()
        
        # Display connection information upon successful initialization
        self._display_connection_info()
    
    def _init_service_clients(self):
        """Initialize all service-specific clients."""
        self.models = ModelsClient(self.session)
        self.deployments = DeploymentsClient(self.session)
        self.preprocessing = PreprocessingClient(self.session)
        self.collections = CollectionsClient(self.session)
        self.datasets = DatasetsClient(self.session)
        self.inference = InferenceClient(self.session)
        self.gpt = GPTClient(self.session)
        self.autotrain = AutotrainClient(self.session)
        self.misc = MiscClient(self.session)
    
    def _display_connection_info(self):
        """Display connection and user information upon client initialization."""
        try:
            user_data = self.session.user_data
            print(f"Connected to Xplainable Cloud")
            print(f"   User: {self.session.username}")
            print(f"   Hostname: {self.session.hostname}")
            print(f"   API Key Expires: {self.session.expires}")
            print(f"   Python Version: {self.session.python_version}")
            print(f"   Xplainable Version: {self.session.xplainable_version}")
            
            # Display organization and team information if available
            if self.session.org_id:
                print(f"   Organization ID: {self.session.org_id}")
            if self.session.team_id:
                print(f"   Team ID: {self.session.team_id}")
                
            # Display additional user info from the user_data if available
            if 'email' in user_data:
                print(f"   Email: {user_data['email']}")
            if 'org_name' in user_data:
                print(f"   Organization: {user_data['org_name']}")
            if 'team_name' in user_data:
                print(f"   Team: {user_data['team_name']}")
                
        except Exception as e:
            print(f"Connected to Xplainable Cloud but failed to retrieve user details: {e}")
    
    @property
    def user_info(self) -> dict:
        """
        Get information about the authenticated user.
        
        Returns:
            Dictionary containing user information
        """
        return self.session.user_data
    
    @property
    def connection_info(self) -> dict:
        """
        Get connection and version information.
        
        Returns:
            Dictionary with connection details and versions
        """
        return {
            "hostname": self.session.hostname,
            "username": self.session.username,
            "api_key_expires": self.session.expires,
            "xplainable_version": self.session.xplainable_version,
            "python_version": self.session.python_version,
            "org_id": self.session.org_id,
            "team_id": self.session.team_id
        }
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return (
            f"XplainableClient("
            f"user='{self.session.username}', "
            f"hostname='{self.session.hostname}'"
            f")"
        )


# For backward compatibility, you could also create an alias
Client = XplainableClient