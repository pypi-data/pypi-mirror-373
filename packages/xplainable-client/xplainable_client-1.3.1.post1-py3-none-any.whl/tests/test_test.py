import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from client.test import foo

def test_foo():
    assert foo(3) == 4, "Should be 4"