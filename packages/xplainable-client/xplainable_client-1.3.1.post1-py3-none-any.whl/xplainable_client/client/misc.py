"""
Refactored misc utilities client using Pydantic models and base client.
"""
from typing import Any, Dict, Optional, Union
import xplainable
from xplainable.utils.model_parsers import parse_classifier_response, parse_regressor_response

from .base import BaseClient, XplainableAPIError
from .py_models.misc import (
    PingResponse,
    VersionInfo,
    ModelLoadRequest,
    LoadedModelInfo,
    ModelPartition,
    HealthCheckRequest,
    HealthCheckResponse,
)


class MiscClient(BaseClient):
    """Client for miscellaneous utilities and model management."""
    
    @staticmethod
    def get_xplainable_version() -> str:
        """
        Get the installed xplainable package version.
        
        Returns:
            Version string
        """
        try:
            return xplainable.__version__
        except AttributeError:
            return "Unknown"
    
    def get_version_info(self) -> VersionInfo:
        """
        Get comprehensive version information.
        
        Returns:
            Version information for all components
        """
        return VersionInfo(
            xplainable_version=self.session.xplainable_version,
            python_version=self.session.python_version,
            client_version=self.get_xplainable_version()
        )
    
    def ping_server(self, hostname: Optional[str] = None) -> PingResponse:
        """
        Ping the compute server to check connectivity.
        
        Args:
            hostname: Optional hostname to ping (uses session hostname if not provided)
            
        Returns:
            Ping response with success status
            
        Raises:
            XplainableAPIError: If ping fails
        """
        if not hostname:
            hostname = self.session.hostname
        
        try:
            import time
            start_time = time.time()
            
            response = self.session._session.get(
                f'{hostname}/v1/compute/ping',
                timeout=5
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    content = response.json()
                    success = content is True or content.get('success', False)
                except:
                    success = True  # If response is not JSON but status is 200
                
                return PingResponse(
                    success=success,
                    response_time=response_time
                )
            else:
                return PingResponse(success=False, response_time=response_time)
                
        except Exception as e:
            raise XplainableAPIError(
                status_code=0,
                message=f"Ping failed: {str(e)}"
            )
    
    def ping_gateway(self, hostname: Optional[str] = None) -> PingResponse:
        """
        Ping the API gateway to check connectivity.
        
        Args:
            hostname: Optional hostname to ping (uses session hostname if not provided)
            
        Returns:
            Ping response with success status
            
        Raises:
            XplainableAPIError: If ping fails
        """
        if not hostname:
            hostname = self.session.hostname
        
        try:
            import time
            start_time = time.time()
            
            response = self.session._session.get(
                f'{hostname}/v1/ping',
                timeout=5
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    content = response.json()
                    success = content is True or content.get('success', False)
                except:
                    success = True
                
                return PingResponse(
                    success=success,
                    response_time=response_time
                )
            else:
                return PingResponse(success=False, response_time=response_time)
                
        except Exception as e:
            raise XplainableAPIError(
                status_code=0,
                message=f"Gateway ping failed: {str(e)}"
            )
    
    def load_classifier(
        self,
        model_id: str,
        version_id: str,
        model=None
    ):
        """
        Load a binary classification model.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            model: Existing model to add partitions to
            
        Returns:
            Loaded xplainable classifier
            
        Raises:
            ValueError: If model is not a classification model
            XplainableAPIError: If loading fails
        """
        response = self._get_model(model_id, version_id)
        
        if response.get('model_type') != 'binary_classification':
            raise ValueError(
                f'Model {model_id}:{version_id} is not a binary classification model'
            )
        
        return parse_classifier_response(response, model)
    
    def load_regressor(
        self,
        model_id: str,
        version_id: str,
        model=None
    ):
        """
        Load a regression model.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            model: Existing model to add partitions to
            
        Returns:
            Loaded xplainable regressor
            
        Raises:
            ValueError: If model is not a regression model
            XplainableAPIError: If loading fails
        """
        response = self._get_model(model_id, version_id)
        
        if response.get('model_type') != 'regression':
            raise ValueError(
                f'Model {model_id}:{version_id} is not a regression model'
            )
        
        return parse_regressor_response(response, model)
    
    def get_model_info(
        self,
        model_id: str,
        version_id: str
    ) -> LoadedModelInfo:
        """
        Get information about a model without loading it.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            
        Returns:
            Model information
            
        Raises:
            XplainableAPIError: If retrieval fails
        """
        response = self._get_model(model_id, version_id)
        
        # Extract key information
        partitions = response.get('partitions', [])
        
        return LoadedModelInfo(
            model_id=model_id,
            version_id=version_id,
            model_type=response.get('model_type', 'unknown'),
            algorithm=response.get('algorithm', 'unknown'),
            target_name=response.get('target_name', 'unknown'),
            feature_count=len(response.get('columns', [])),
            partition_count=len(partitions),
            metadata=response.get('metadata', {})
        )
    
    def health_check(
        self,
        check_database: bool = True,
        check_storage: bool = True,
        check_compute: bool = True
    ) -> HealthCheckResponse:
        """
        Perform a comprehensive health check.
        
        Args:
            check_database: Whether to check database connectivity
            check_storage: Whether to check storage systems
            check_compute: Whether to check compute resources
            
        Returns:
            Health check results
            
        Raises:
            XplainableAPIError: If health check fails
        """
        request = HealthCheckRequest(
            check_database=check_database,
            check_storage=check_storage,
            check_compute=check_compute
        )
        
        # Note: This endpoint would need to be added to the API
        url = f"{self.session.hostname}/v1/health"
        response = self.session._session.post(
            url=url,
            json=request.model_dump()
        )
        
        result = self._handle_response(response, HealthCheckResponse)
        return result
    
    def _get_model(self, model_id: str, version_id: str) -> Dict[str, Any]:
        """
        Internal method to get model data.
        
        Args:
            model_id: Model ID
            version_id: Version ID
            
        Returns:
            Model data dictionary
            
        Raises:
            XplainableAPIError: If retrieval fails
        """
        # This would typically use the models client, but for compatibility
        # we'll implement it here
        url = f"{self.session.hostname}/v1/client/models/{model_id}/versions/{version_id}/full"
        response = self.session._session.get(url=url)
        
        return self._handle_response(response)
    
    def parse_function(self, func) -> Any:
        """
        Parse a function to a middleware function.
        
        This is a utility method from the original implementation.
        
        Args:
            func: Function to parse
            
        Returns:
            Parsed middleware function
            
        Raises:
            ValueError: If function is invalid
        """
        if not callable(func):
            raise ValueError("Function must be callable")
        
        import inspect
        import ast
        
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        if len(params) != 1:
            raise ValueError("Function must take one parameter")
        
        # Parse the source code to an AST
        source = inspect.getsource(func)
        parsed_ast = ast.parse(source)
        
        # Rename the function in the AST
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
                node.name = "middleware"
                break
        
        # Store the modified source
        modified_source = ast.unparse(parsed_ast)
        
        # Compile the AST back to code and execute in a new namespace
        local_vars = {}
        exec(compile(
            parsed_ast, filename="<ast>", mode="exec"),
            func.__globals__, local_vars)
        
        middleware = local_vars['middleware']
        middleware.source = modified_source
        return middleware