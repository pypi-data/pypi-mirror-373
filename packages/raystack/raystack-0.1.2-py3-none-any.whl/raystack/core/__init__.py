try:
    from . import database
except ImportError as e:
    # Log the error but don't fail completely
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to import database module: {e}")

from . import security
from . import dependencies