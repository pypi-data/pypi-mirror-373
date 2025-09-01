"""
Refactored GPT/LLM client using Pydantic models and base client.
"""
from typing import Dict, Optional

from .base import BaseClient
from .py_models.gpt import (
    GPTReportRequest,
    GPTReportResponse,
    ModelExplanationRequest,
    ModelExplanationResponse,
)
from .utils.constants import GPT_ENDPOINTS


class GPTClient(BaseClient):
    """Client for GPT/LLM-powered features."""
    
    def generate_report(
        self,
        model_id: str,
        version_id: str,
        target_description: str = "text",
        project_objective: str = "text",
        max_features: int = 15,
        temperature: float = 0.7
    ) -> GPTReportResponse:
        """
        Generate a GPT-powered report for a model.
        
        Args:
            model_id: ID of the model
            version_id: ID of the model version
            target_description: Description of the target variable
            project_objective: Objective of the project/model
            max_features: Maximum number of features to include in report
            temperature: GPT temperature parameter (0-2, higher = more creative)
            
        Returns:
            Generated report with insights
            
        Raises:
            XplainableAPIError: If report generation fails
        """
        request = GPTReportRequest(
            model_version_id=version_id,
            target_description=target_description,
            project_objective=project_objective,
            max_features=max_features,
            temperature=temperature
        )
        
        return self.post(
            GPT_ENDPOINTS["generate_report"],
            data=request,
            response_model=GPTReportResponse
        )
    
    def explain_model(
        self,
        model_id: str,
        version_id: str,
        language: str = "en",
        detail_level: str = "medium"
    ) -> ModelExplanationResponse:
        """
        Get a natural language explanation of the model.
        
        Args:
            model_id: ID of the model
            version_id: ID of the model version
            language: Language for the explanation (e.g., "en", "es", "fr")
            detail_level: Level of detail ("low", "medium", "high")
            
        Returns:
            Natural language explanation of the model
            
        Raises:
            XplainableAPIError: If explanation generation fails
        """
        request = ModelExplanationRequest(
            model_version_id=version_id,
            language=language,
            detail_level=detail_level
        )
        
        return self.post(
            GPT_ENDPOINTS["explain_model"],
            data=request,
            response_model=ModelExplanationResponse
        )
    
    def generate_documentation(
        self,
        model_id: str,
        version_id: str,
        include_technical: bool = True,
        include_business: bool = True,
        format: str = "markdown"
    ) -> str:
        """
        Generate comprehensive documentation for a model.
        
        Args:
            model_id: ID of the model
            version_id: ID of the model version
            include_technical: Include technical details
            include_business: Include business context
            format: Output format ("markdown", "html", "pdf")
            
        Returns:
            Generated documentation
            
        Raises:
            XplainableAPIError: If documentation generation fails
        """
        request = {
            'include_technical': include_technical,
            'include_business': include_business,
            'format': format
        }
        
        url = f"{self.session.hostname}/v1/client/models/{model_id}/versions/{version_id}/documentation"
        
        response = self.session._session.post(
            url=url,
            json=request
        )
        
        result = self._handle_response(response)
        
        if isinstance(result, dict):
            return result.get('documentation', str(result))
        return str(result)
    