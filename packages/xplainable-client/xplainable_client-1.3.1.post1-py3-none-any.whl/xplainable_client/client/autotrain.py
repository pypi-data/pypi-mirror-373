"""
Refactored autotrain client using Pydantic models and base client.
"""
from typing import Dict, Any, Optional, List, Union
import json

from .base import BaseClient, XplainableAPIError
from .py_models.autotrain import (
    DatasetSummary,
    TextGenConfig,
    TrainingGoal,
    LabelRecommendation,
    FeatureEngineeringRecommendation,
    AutotrainRequest,
    AutotrainResponse,
    TrainingStatus,
    ManualTrainRequest,
    VisualizationRequest,
    VisualizationResponse,
)
from .utils.constants import AUTOTRAIN_ENDPOINTS


class AutotrainClient(BaseClient):
    """Client for automated training workflows."""
    
    def summarize_dataset(
        self,
        file_path: str,
        team_id: Optional[str] = None,
        textgen_config: Optional[TextGenConfig] = None
    ) -> DatasetSummary:
        """
        Summarize a dataset by uploading a file.
        
        Args:
            file_path: Path to the dataset file
            team_id: Team ID (uses session team_id if not provided)
            textgen_config: Text generation configuration
            
        Returns:
            Dataset summary and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            XplainableAPIError: If summarization fails
        """
        if not team_id:
            team_id = self.session.team_id
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {
                    'team_id': team_id,
                    'textgen_config': textgen_config.model_dump_json() if textgen_config else None
                }
                
                response = self.session._session.post(
                    url=f"{self.session.hostname}{AUTOTRAIN_ENDPOINTS['summarize']}",
                    files=files,
                    data=data
                )
                
                result = self._handle_response(response)
                return DatasetSummary(**result)
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        except Exception as e:
            raise XplainableAPIError(
                status_code=0,
                message=f"Failed to summarize dataset: {str(e)}"
            )
    
    def generate_goals(
        self,
        summary: DatasetSummary,
        team_id: Optional[str] = None,
        n: int = 5,
        textgen_config: Optional[TextGenConfig] = None
    ) -> List[TrainingGoal]:
        """
        Generate training goals based on dataset summary.
        
        Args:
            summary: Dataset summary from summarize_dataset
            team_id: Team ID (uses session team_id if not provided)
            n: Number of goals to generate
            textgen_config: Text generation configuration
            
        Returns:
            List of training goals
            
        Raises:
            XplainableAPIError: If goal generation fails
        """
        if not team_id:
            team_id = self.session.team_id
        
        request = {
            "team_id": team_id,
            "req": {
                "summary": summary.model_dump(),
                "n": n,
                "textgen_config": textgen_config.model_dump() if textgen_config else {}
            }
        }
        
        response = self.session._session.post(
            url=f"{self.session.hostname}{AUTOTRAIN_ENDPOINTS['generate_goals']}",
            json=request
        )
        
        result = self._handle_response(response)
        
        # Parse goals
        if isinstance(result, dict) and 'goals' in result:
            return [TrainingGoal(**goal) for goal in result['goals']]
        elif isinstance(result, list):
            return [TrainingGoal(**goal) for goal in result]
        return []
    
    def generate_labels(
        self,
        summary: DatasetSummary,
        team_id: Optional[str] = None,
        textgen_config: Optional[TextGenConfig] = None
    ) -> List[LabelRecommendation]:
        """
        Generate label recommendations for training.
        
        Args:
            summary: Dataset summary from summarize_dataset
            team_id: Team ID (uses session team_id if not provided)
            textgen_config: Text generation configuration
            
        Returns:
            List of label recommendations
            
        Raises:
            XplainableAPIError: If label generation fails
        """
        if not team_id:
            team_id = self.session.team_id
        
        request = {
            "team_id": team_id,
            "req": {
                "summary": summary.model_dump(),
                "textgen_config": textgen_config.model_dump() if textgen_config else {}
            }
        }
        
        response = self.session._session.post(
            url=f"{self.session.hostname}{AUTOTRAIN_ENDPOINTS['generate_labels']}",
            json=request
        )
        
        result = self._handle_response(response)
        
        # Parse labels
        if isinstance(result, dict) and 'labels' in result:
            return [LabelRecommendation(**label) for label in result['labels']]
        elif isinstance(result, list):
            return [LabelRecommendation(**label) for label in result]
        return []
    
    def generate_feature_engineering(
        self,
        summary: DatasetSummary,
        team_id: Optional[str] = None,
        n: int = 5,
        textgen_config: Optional[TextGenConfig] = None
    ) -> List[FeatureEngineeringRecommendation]:
        """
        Generate feature engineering recommendations.
        
        Args:
            summary: Dataset summary from summarize_dataset
            team_id: Team ID (uses session team_id if not provided)
            n: Number of recommendations to generate
            textgen_config: Text generation configuration
            
        Returns:
            List of feature engineering recommendations
            
        Raises:
            XplainableAPIError: If generation fails
        """
        if not team_id:
            team_id = self.session.team_id
        
        request = {
            "team_id": team_id,
            "req": {
                "summary": summary.model_dump(),
                "n": n,
                "textgen_config": textgen_config.model_dump() if textgen_config else {}
            }
        }
        
        response = self.session._session.post(
            url=f"{self.session.hostname}{AUTOTRAIN_ENDPOINTS['generate_feature_engineering']}",
            json=request
        )
        
        result = self._handle_response(response)
        
        # Parse recommendations
        if isinstance(result, dict) and 'recommendations' in result:
            return [FeatureEngineeringRecommendation(**rec) for rec in result['recommendations']]
        elif isinstance(result, list):
            return [FeatureEngineeringRecommendation(**rec) for rec in result]
        return []
    
    def start_autotrain(
        self,
        model_name: str,
        model_description: str,
        summary: DatasetSummary,
        team_id: Optional[str] = None,
        textgen_config: Optional[TextGenConfig] = None
    ) -> AutotrainResponse:
        """
        Start the autotrain process.
        
        Args:
            model_name: Name for the model
            model_description: Description of the model
            summary: Dataset summary from summarize_dataset
            team_id: Team ID (uses session team_id if not provided)
            textgen_config: Text generation configuration
            
        Returns:
            Training job information
            
        Raises:
            XplainableAPIError: If autotrain fails to start
        """
        if not team_id:
            team_id = self.session.team_id
        
        request = AutotrainRequest(
            model_name=model_name,
            model_description=model_description,
            summary=summary,
            team_id=team_id,
            textgen_config=textgen_config
        )
        
        payload = {
            "team_id": team_id,
            "req": {
                "model_name": model_name,
                "model_description": model_description,
                "summary": summary.model_dump(),
                "textgen_config": textgen_config.model_dump() if textgen_config else {}
            }
        }
        
        response = self.session._session.post(
            url=f"{self.session.hostname}{AUTOTRAIN_ENDPOINTS['start_autotrain']}",
            json=payload
        )
        
        result = self._handle_response(response, AutotrainResponse)
        return result
    
    def check_training_status(
        self,
        training_id: str,
        team_id: Optional[str] = None
    ) -> TrainingStatus:
        """
        Check the status of a training job.
        
        Args:
            training_id: Training job ID from start_autotrain
            team_id: Team ID (uses session team_id if not provided)
            
        Returns:
            Training status and progress information
            
        Raises:
            XplainableAPIError: If status check fails
        """
        if not team_id:
            team_id = self.session.team_id
        
        response = self.session._session.get(
            url=f"{self.session.hostname}{AUTOTRAIN_ENDPOINTS['check_training_status'].replace('{training_id}', training_id)}",
            params={'team_id': team_id}
        )
        
        result = self._handle_response(response, TrainingStatus)
        return result
    
    def train_manual(
        self,
        label: str,
        model_name: str,
        model_description: str,
        preprocessor_id: str,
        version_id: str,
        team_id: Optional[str] = None,
        drop_columns: Optional[List[str]] = None
    ) -> AutotrainResponse:
        """
        Train a model manually with specific parameters.
        
        Args:
            label: Target label column
            model_name: Name for the model
            model_description: Description of the model
            preprocessor_id: Preprocessor ID
            version_id: Preprocessor version ID
            team_id: Team ID (uses session team_id if not provided)
            drop_columns: Columns to drop
            
        Returns:
            Training job information
            
        Raises:
            XplainableAPIError: If training fails to start
        """
        if not team_id:
            team_id = self.session.team_id
        
        request = ManualTrainRequest(
            label=label,
            model_name=model_name,
            model_description=model_description,
            preprocessor_id=preprocessor_id,
            version_id=version_id,
            team_id=team_id,
            drop_columns=drop_columns
        )
        
        payload = {
            "team_id": team_id,
            "req": request.model_dump(exclude={'team_id'})
        }
        
        response = self.session._session.post(
            url=f"{self.session.hostname}{AUTOTRAIN_ENDPOINTS['train_manual']}",
            json=payload
        )
        
        result = self._handle_response(response, AutotrainResponse)
        return result
    
    def visualize_data(
        self,
        summary: DatasetSummary,
        goal: Dict[str, Any],
        team_id: Optional[str] = None,
        library: str = "plotly",
        textgen_config: Optional[TextGenConfig] = None
    ) -> VisualizationResponse:
        """
        Generate data visualizations.
        
        Args:
            summary: Dataset summary
            goal: Visualization goal
            team_id: Team ID (uses session team_id if not provided)
            library: Visualization library (plotly, matplotlib, seaborn)
            textgen_config: Text generation configuration
            
        Returns:
            Visualization code and metadata
            
        Raises:
            XplainableAPIError: If visualization generation fails
        """
        if not team_id:
            team_id = self.session.team_id
        
        request = VisualizationRequest(
            summary=summary,
            goal=goal,
            team_id=team_id,
            library=library,
            textgen_config=textgen_config
        )
        
        payload = {
            "team_id": team_id,
            "req": {
                "summary": summary.model_dump(),
                "goal": goal,
                "library": library,
                "textgen_config": textgen_config.model_dump() if textgen_config else {}
            }
        }
        
        # Note: This endpoint might not exist yet in the API
        url = f"{self.session.hostname}/v1/client/autotrain/visualize"
        response = self.session._session.post(url=url, json=payload)
        
        result = self._handle_response(response, VisualizationResponse)
        return result
    
    def generate_insights(
        self,
        goal: Dict[str, Any],
        summary: DatasetSummary,
        team_id: Optional[str] = None,
        textgen_config: Optional[TextGenConfig] = None
    ) -> Dict[str, Any]:
        """
        Generate insights about the dataset.
        
        Args:
            goal: Analysis goal
            summary: Dataset summary
            team_id: Team ID (uses session team_id if not provided)
            textgen_config: Text generation configuration
            
        Returns:
            Generated insights and analysis
            
        Raises:
            XplainableAPIError: If insight generation fails
        """
        if not team_id:
            team_id = self.session.team_id
        
        payload = {
            "team_id": team_id,
            "req": {
                "goal": goal,
                "summary": summary.model_dump(),
                "textgen_config": textgen_config.model_dump() if textgen_config else {}
            }
        }
        
        url = f"{self.session.hostname}/v1/client/autotrain/insights"
        response = self.session._session.post(url=url, json=payload)
        
        return self._handle_response(response)