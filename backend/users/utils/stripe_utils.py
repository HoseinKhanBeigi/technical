"""
Stripe utility functions for initializing and managing Stripe API.

This module provides a singleton pattern for Stripe initialization
to avoid multiple imports and ensure API key is set correctly.
"""
from typing import Dict, List, Optional, Any
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Lazy import Stripe to avoid initialization issues
_stripe_module: Optional[Any] = None


def get_stripe() -> Any:
    """
    Get Stripe module with API key configured (singleton pattern).
    
    Returns:
        stripe: Initialized Stripe module with API key set
        
    Raises:
        ValueError: If STRIPE_SECRET_KEY is not configured or initialization fails
    """
    global _stripe_module
    
    if _stripe_module is None:
        if not settings.STRIPE_SECRET_KEY:
            raise ValueError("STRIPE_SECRET_KEY is not set in environment variables")
        
        try:
            import stripe
            # Set API key immediately after import
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Verify the key is set
            if not stripe.api_key:
                raise ValueError("Failed to set Stripe API key")
            
            _stripe_module = stripe
            logger.info("Stripe module initialized successfully")
            
        except ImportError as e:
            raise ValueError(f"Failed to import Stripe library: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to initialize Stripe: {str(e)}")
    elif not _stripe_module.api_key and settings.STRIPE_SECRET_KEY:
        _stripe_module.api_key = settings.STRIPE_SECRET_KEY
    
    return _stripe_module


def get_plan_price_ids() -> Dict[str, Optional[str]]:
    """
    Get mapping of plan names to Stripe price IDs.
    
    Returns:
        dict: Mapping of plan names to price IDs
            {
                'basic': settings.STRIPE_BASIC_PLAN_PRICE_ID,
                'pro': settings.STRIPE_PRO_PLAN_PRICE_ID,
            }
    """
    return {
        'basic': settings.STRIPE_BASIC_PLAN_PRICE_ID,
        'pro': settings.STRIPE_PRO_PLAN_PRICE_ID,
    }


def validate_stripe_config() -> List[str]:
    """
    Validate that Stripe is properly configured.
    
    Returns:
        list: List of configuration errors (empty if all valid)
        
    Example:
        >>> errors = validate_stripe_config()
        >>> if errors:
        ...     print(f"Configuration errors: {errors}")
    """
    errors: List[str] = []
    
    if not settings.STRIPE_SECRET_KEY:
        errors.append('STRIPE_SECRET_KEY is not set')
    
    price_ids = get_plan_price_ids()
    if not price_ids.get('basic'):
        errors.append('STRIPE_BASIC_PLAN_PRICE_ID is not set')
    if not price_ids.get('pro'):
        errors.append('STRIPE_PRO_PLAN_PRICE_ID is not set')
    
    if errors:
        logger.warning(f"Stripe configuration errors: {errors}")
    
    return errors

