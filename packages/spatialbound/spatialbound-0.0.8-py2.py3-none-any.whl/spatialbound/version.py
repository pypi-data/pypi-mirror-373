# spatialbound/version.py
"""
Version information for the Spatialbound package.
"""
import pkg_resources
import logging

logger = logging.getLogger(__name__)

try:
    # Read version from installed package metadata
    __version__ = pkg_resources.get_distribution("spatialbound").version
except pkg_resources.DistributionNotFound:
    __version__ = "0.0.8" 
    logger.warning("Spatialbound package not installed, using default version")