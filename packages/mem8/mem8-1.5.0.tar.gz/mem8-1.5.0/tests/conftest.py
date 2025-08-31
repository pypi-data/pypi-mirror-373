"""
Pytest configuration for AI-Mem tests.
"""

import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import ai_mem
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace for testing."""
    workspace = tmp_path / "workspace"
    shared = tmp_path / "shared"
    
    workspace.mkdir()
    shared.mkdir()
    
    return {
        'workspace': workspace,
        'shared': shared,
        'tmp_path': tmp_path
    }