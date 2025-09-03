"""RepoPi - An all-in-one developer assistant for Git workflows, hosting, and AI automation.

RepoPi streamlines everyday Git workflows and integrates Git hosting features,
AI automation, and team productivity tools—directly in the terminal.
"""

__version__ = "0.1.1"
__author__ = "S M Asiful Islam Saky"
__email__ = "saky.aiu22@gmail.com"
__description__ = "An all-in-one developer assistant for Git workflows, hosting, and AI automation."
__homepage__ = "https://pypi.org/project/repopi/"
__repository__ = "https://github.com/saky-semicolon/repopi"
__license__ = "MIT"

# Public API
from repopi.main import app

__all__ = ["app", "__version__"]