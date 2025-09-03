"""
Convenience module for importing {LIBRARY_NAME}.

This allows users to import the library in two ways:
1. import exonware.{LIBRARY_NAME}
2. import {LIBRARY_NAME}  # This convenience import

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: {GENERATION_DATE}
"""

# Import everything from the main package
from exonware.LIBRARY_NAME import *  # noqa: F401, F403

# Preserve the version
__version__ = "0.0.1"