import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from client._models import Models

def test_list_models():
    assert Models.list_models() == ['model1', 'model2', 'model3'], "Should be ['model1', 'model2', 'model3']"