"""
Refactored inference client using Pydantic models and base client.
"""
import pandas as pd
from typing import Union
from .base import BaseClient, XplainableAPIError
from .utils.constants import INFERENCE_ENDPOINTS


class InferenceClient(BaseClient):
    """Client for model inference and predictions."""
    
    def predict(self, filename: str, model_id: str, version_id: str, threshold: float = 0.5, delimiter: str = ","):
        """
        Predicts the target column of a dataset.
        
        Args:
            filename (str): The name of the file.
            model_id (str): The model id.
            version_id (str): The version id.
            threshold (float): The threshold for classification models.
            delimiter (str): The delimiter of the file.
            
        Returns:
            dict: The prediction results.
        """
        url = self._build_url(INFERENCE_ENDPOINTS["predict"])
        try:
            files = {'file': open(filename, 'rb')}
        except Exception:
            raise ValueError(f'Unable to open file {filename}. Check the file path and try again.')
        form = {'model_id': model_id, 'version_id': version_id, 'threshold': threshold, 'delimiter': delimiter}
        
        try:
            response = self.session._session.post(url, files=files, form=form)
        except Exception as e:
            raise ValueError(f'{e}. Please contact us if this problem persists.')
        
        # Use the session's response handler to match old behavior
        data = self.session.get_response_content(response)
        return data
    
    def stream_predictions(
        self,
        filename: str,
        model_id: str,
        version_id: str,
        threshold: float = 0.5,
        delimiter: str = ",",
        batch_size: int = 1000
    ):
        """
        Stream predictions for large datasets by processing in batches.
        
        Args:
            filename: Path to CSV file to stream
            model_id: ID of the model
            version_id: ID of the model version
            threshold: Classification threshold
            delimiter: CSV delimiter
            batch_size: Size of each batch to process
            
        Yields:
            Batch prediction results
        """
        # Read file in chunks
        try:
            for chunk in pd.read_csv(filename, delimiter=delimiter, chunksize=batch_size):
                # Save chunk to temporary file
                temp_file = f"/tmp/batch_{chunk.index[0]}.csv"
                chunk.to_csv(temp_file, index=False, sep=delimiter)
                
                # Use existing predict method for each batch
                result = self.predict(
                    filename=temp_file,
                    model_id=model_id,
                    version_id=version_id,
                    threshold=threshold,
                    delimiter=delimiter
                )
                
                # Clean up temp file
                import os
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                yield result
                
        except Exception as e:
            raise ValueError(f'Unable to stream file {filename}: {e}')