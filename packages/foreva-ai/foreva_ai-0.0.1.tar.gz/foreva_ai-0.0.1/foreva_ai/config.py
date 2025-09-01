"""
Foreva SDK Configuration
Pure pass-through configuration with build-specific logging
"""

import os

# Build configuration
BUILD_ENV = os.environ.get('FOREVA_BUILD_ENV', 'production')

# Environment-specific defaults
def get_default_base_url():
    """Get default API URL based on build environment"""
    if BUILD_ENV == 'staging':
        return 'https://dishpop.co/api/v1/sdk'
    else:
        return 'https://foreva.ai/api/v1/sdk'

BASE_URL = os.environ.get('FOREVA_API_URL', get_default_base_url())

def get_base_url() -> str:
    """Get API base URL"""
    return BASE_URL

def is_debug_build() -> bool:
    """Check if this is a debug build"""
    return BUILD_ENV == 'staging'

def should_show_internal_logs() -> bool:
    """Show detailed internal logs for debug builds"""
    return is_debug_build()

def should_show_urls() -> bool:
    """Show API URLs for debug builds"""
    return is_debug_build()

def should_show_detailed_errors() -> bool:
    """Show detailed error info for debug builds"""
    return is_debug_build()