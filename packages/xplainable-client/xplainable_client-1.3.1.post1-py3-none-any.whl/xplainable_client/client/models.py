"""
Refactored models client using Pydantic models and base client.
"""
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from xplainable.utils.encoders import force_json_compliant

from .base import BaseClient
from .py_models.models import (
    CreateModelRequest,
    CreateModelResponse,
    AddVersionRequest,
    AddVersionResponse,
    ModelInfo,
    ModelVersion,
)
from .utils.constants import MODEL_ENDPOINTS


class ModelsClient(BaseClient):
    """Client for managing ML models."""
    
    def create_model(
        self,
        model,
        model_name: str,
        model_description: str,
        x: pd.DataFrame,
        y: pd.Series
    ) -> Tuple[str, str]:
        """
        Create a new model.
        
        Args:
            model: The XClassifier or XRegressor model
            model_name: Name of the model
            model_description: Description of the model
            x: Feature matrix
            y: Target variable
            
        Returns:
            Tuple of (model_id, version_id)
            
        Raises:
            XplainableAPIError: If model creation fails
        """
        model_type, target = self._detect_model_type(model)
        partition_on = model.partition_on if 'Partitioned' in model.__class__.__name__ else None
        
        # Build partitions data
        partitions = self._build_partitions_data(model, partition_on, x, y)
        
        # Create request
        request = CreateModelRequest(
            name=model_name,
            description=model_description,
            type=model_type,
            target_name=target,
            algorithm=model.__class__.__name__,
            partition_on=partition_on,
            versions={
                "xplainable_version": self.session.xplainable_version,
                "python_version": self.session.python_version
            },
            partitions=partitions
        )
        
        # Make request with custom JSON encoding for numpy/pandas objects
        url = self._build_url(MODEL_ENDPOINTS["create"])
        payload = force_json_compliant(request.model_dump(exclude_none=True))
        
        response = self.session._session.post(url=url, json=payload)
        
        # Handle the response - match old client behavior
        if response.status_code == 200:
            # Old client returns the entire content dict
            content = response.json()
            # Check if it's the new format with model_id and version_id
            if 'model_id' in content and 'version_id' in content:
                return content['model_id'], content['version_id']
            # Otherwise return the whole dict (old client behavior)
            return content
        else:
            # Let the error handler deal with it
            content = self._handle_response(response, CreateModelResponse)
            return content.model_id, content.version_id
    
    def add_version(
        self,
        model,
        model_id: str,
        x: pd.DataFrame,
        y: pd.Series
    ) -> str:
        """
        Add a new version to an existing model.
        
        Args:
            model: The XClassifier or XRegressor model
            model_id: ID of the existing model
            x: Feature matrix
            y: Target variable
            
        Returns:
            The new version_id
            
        Raises:
            XplainableAPIError: If version addition fails
        """
        partition_on = model.partition_on if 'Partitioned' in model.__class__.__name__ else None
        
        # Build partitions data
        partitions = self._build_partitions_data(model, partition_on, x, y)
        
        # Create request
        request = AddVersionRequest(
            model_id=model_id,
            partition_on=partition_on,
            versions={
                "xplainable_version": self.session.xplainable_version,
                "python_version": self.session.python_version
            },
            partitions=partitions
        )
        
        # Make request with custom JSON encoding
        response = self.session._session.post(
            url=self._build_url(MODEL_ENDPOINTS["add_version"]),
            json=force_json_compliant(request.model_dump(exclude_none=True))
        )
        
        content = self._handle_response(response, AddVersionResponse)
        return content.version_id
    
    def list_team_models(self) -> List[ModelInfo]:
        """
        List all models for the current team (based on API key).
        
        Returns:
            List of model information
            
        Raises:
            XplainableAPIError: If listing fails
        """
        response = self.get(MODEL_ENDPOINTS["list_team_models"])
        
        # Parse response into list of ModelInfo models
        return [ModelInfo(**item) for item in response]
    
    def get_model(self, model_id: str) -> ModelInfo:
        """
        Get detailed information about a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Model information
            
        Raises:
            XplainableAPIError: If retrieval fails
        """
        return self.get(
            MODEL_ENDPOINTS["get_model"],
            response_model=ModelInfo,
            model_id=model_id
        )
    
    def list_model_versions(self, model_id: str) -> List[ModelVersion]:
        """
        List all versions of a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            List of model versions
            
        Raises:
            XplainableAPIError: If listing fails
        """
        response = self.get(
            MODEL_ENDPOINTS["list_versions"],
            model_id=model_id
        )
        
        # Parse response into list of ModelVersion models
        return [ModelVersion(**item) for item in response]
    
    def list_model_version_partitions(self, version_id: str) -> Dict[str, Any]:
        """
        List all partitions for a model version.
        
        Args:
            version_id: ID of the model version (or "latest")
            
        Returns:
            Dictionary containing partition information
            
        Raises:
            XplainableAPIError: If listing fails
        """
        return self.get(
            MODEL_ENDPOINTS["list_partitions"],
            version_id=version_id
        )
    
    def link_preprocessor(
        self,
        model_version_id: str,
        preprocessor_version_id: str
    ) -> None:
        """
        Link a model version to a preprocessor version.
        
        Args:
            model_version_id: The model version ID
            preprocessor_version_id: The preprocessor version ID
            
        Raises:
            XplainableAPIError: If linking fails
        """
        payload = {
            "version_id": model_version_id,  # API expects "version_id" for model version
            "preprocessor_version_id": preprocessor_version_id
        }
        
        url = self._build_url(MODEL_ENDPOINTS["link_preprocessor"])
        response = self.session._session.put(url=url, json=payload)
        
        # Handle successful response with potentially empty content
        if response.status_code >= 200 and response.status_code < 300:
            # Check if response has content
            try:
                if response.content:
                    data = response.json()
                    return data if data else {}
                return {}  # Return empty dict for successful empty responses
            except:
                return {}  # Return empty dict if JSON parsing fails
        else:
            # Handle errors normally
            self._handle_response(response, dict)
    
    # Helper methods (private)
    
    def _detect_model_type(self, model) -> Tuple[str, str]:
        """
        Detect the model type and target variable name.
        
        Args:
            model: The model object
            
        Returns:
            Tuple of (model_type, target_name)
        """
        # Handle partitioned models
        if 'Partitioned' in model.__class__.__name__:
            model = model.partitions['__dataset__']
        
        cls_name = model.__class__.__name__
        if cls_name == "XClassifier":
            model_type = "binary_classification"
        elif cls_name == "XRegressor":
            model_type = "regression"
        else:
            raise ValueError(f'Model type {cls_name} is not supported')
        
        return model_type, model.target
    
    def _build_partitions_data(
        self,
        model,
        partition_on: Optional[str],
        x: pd.DataFrame,
        y: pd.Series
    ) -> List[Dict[str, Any]]:
        """
        Build partitions data for model creation/versioning.
        
        Args:
            model: The model object
            partition_on: Partition column name
            x: Feature matrix
            y: Target variable
            
        Returns:
            List of partition data dictionaries
        """
        partitions = []
        partitioned_models = ['PartitionedClassifier', 'PartitionedRegressor']
        independent_models = ['XClassifier', 'XRegressor']
        
        if model.__class__.__name__ in partitioned_models:
            for p, m in model.partitions.items():
                if p == '__dataset__':
                    part_x = x
                    part_y = y
                else:
                    part_x = x[x[partition_on].astype(str) == str(p)]
                    part_y = y[y.index.isin(part_x.index)]
                pdata = self._get_partition_data(m, p, part_x, part_y)
                partitions.append(pdata)
                
        elif model.__class__.__name__ in independent_models:
            pdata = self._get_partition_data(model, '__dataset__', x, y)
            partitions.append(pdata)
            
        return partitions
    
    def _get_partition_data(
        self,
        model,
        partition_name: str,
        x: pd.DataFrame,
        y: pd.Series
    ) -> Dict[str, Any]:
        """
        Get partition data for a single partition.
        
        Matches the exact format of the old _models.py implementation.
        """
        import json
        from xplainable.utils.encoders import NpEncoder
        from xplainable.metrics.metrics import evaluate_classification, evaluate_regression
        
        model_type, _ = self._detect_model_type(model)
        
        # Build the core model data - exactly as old client
        data = {
            "partition": str(partition_name),
            "profile": json.dumps(model._profile, cls=NpEncoder),  # Keep as JSON string
            "feature_importances": json.loads(
                json.dumps(model.feature_importances, cls=NpEncoder)),
            "id_columns": json.loads(
                json.dumps(model.id_columns, cls=NpEncoder)),
            "columns": json.loads(
                json.dumps(model.columns, cls=NpEncoder)),
            "parameters": model.params.to_json(),
            "base_value": json.loads(
                json.dumps(model.base_value, cls=NpEncoder)),
            "feature_map": json.loads(
                json.dumps({k: fm.forward for k, fm in model.feature_map.items()}, cls=NpEncoder)),
            "target_map": json.loads(
                json.dumps(model.target_map.reverse, cls=NpEncoder)),
            "category_meta": json.loads(
                json.dumps(model.category_meta, cls=NpEncoder)),
            "calibration_map": None,
            "support_map": None
        }
        
        # Use exact same model type check as old client
        if model_type == 'binary_classification':
            data.update({
                "calibration_map": json.loads(
                    json.dumps(model._calibration_map, cls=NpEncoder)),
                "support_map": json.loads(
                    json.dumps(model._support_map, cls=NpEncoder))
            })
            
            evaluation = model.metadata.get('evaluation', {})
            if evaluation == {}:
                y_prob = model.predict_score(x)
                
                if model.target_map:
                    y = y.map(model.target_map)
                
                evaluation = {
                    'train': evaluate_classification(y, y_prob)
                }
        
        elif model_type == 'regression':
            evaluation = model.metadata.get('evaluation', {})
            if evaluation == {}:
                y_pred = model.predict(x)
                evaluation = {
                    'train': evaluate_regression(y, y_pred)
                }
        else:
            evaluation = {}
        
        # IMPORTANT: evaluation must be JSON string, not dict
        data["evaluation"] = json.dumps(evaluation, cls=NpEncoder)
        
        # Add training_metadata field (required by server)
        training_metadata = {
            i: v for i, v in model.metadata.items() if i != "evaluation"} if hasattr(model, 'metadata') else {}
        
        data["training_metadata"] = json.dumps(training_metadata, cls=NpEncoder)
        
        # Add health_info - server always expects this field
        if x is not None:
            from xplainable.quality.scanner import XScan
            scanner = XScan()
            scanner.scan(x)
            
            results = []
            for i, v in scanner.profile.items():
                feature_info = {
                    "feature": i,
                    "description": '',
                    "type": v['type'],
                    "health_info": json.loads(json.dumps(v, cls=NpEncoder))
                }
                results.append(feature_info)
            
            data["health_info"] = json.dumps(results, cls=NpEncoder)
        else:
            # Provide empty health_info if x is None
            data["health_info"] = json.dumps([], cls=NpEncoder)
        
        return data