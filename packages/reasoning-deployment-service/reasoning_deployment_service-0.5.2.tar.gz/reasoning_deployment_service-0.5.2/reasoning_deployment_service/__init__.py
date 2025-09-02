# Initialize the reasoning_deployment_service package

from .reasoning_deployment_service import ReasoningEngineDeploymentService

# Import submodules for optional use
try:
    from . import cli_editor
    from . import gui_editor
    CLI_AVAILABLE = True
    GUI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some optional components not available: {e}")
    CLI_AVAILABLE = False
    GUI_AVAILABLE = False

# Make main classes available for direct import
__all__ = [
    'ReasoningEngineDeploymentService',
]

# Add optional components if available
if CLI_AVAILABLE:
    __all__.append('cli_editor')
if GUI_AVAILABLE:
    __all__.append('gui_editor')
