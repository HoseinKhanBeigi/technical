"""
User service for handling user data operations.

This service encapsulates all user-related business logic,
separating it from view layer concerns.
"""
import logging
from typing import Dict, Optional
from django.contrib.auth import get_user_model
from ..models import User
from ..serializers import UserSerializer

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class UserService:
    """
    Service for handling user data operations.
    
    Provides methods for retrieving, updating, and serializing user data.
    """
    
    @staticmethod
    def get_user_status(user: User) -> Dict:
        """
        Get user status including subscription information.
        
        Args:
            user: User instance to get status for
            
        Returns:
            Dictionary containing serialized user data with subscription status
            
        Raises:
            ValueError: If user is None
        """
        if user is None:
            raise ValueError("User cannot be None")
        
        serializer = UserSerializer(user)
        logger.debug(f"Retrieved user status for {user.username}")
        return serializer.data
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID.
        
        Args:
            user_id: User ID to look up
            
        Returns:
            User instance if found, None otherwise
        """
        try:
            user = UserModel.objects.get(pk=user_id)
            logger.debug(f"Retrieved user by ID: {user_id}")
            return user
        except UserModel.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by ID {user_id}: {e}")
            raise
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Retrieve a user by their username.
        
        Args:
            username: Username to look up
            
        Returns:
            User instance if found, None otherwise
        """
        if not username:
            return None
        
        try:
            user = UserModel.objects.get(username=username)
            logger.debug(f"Retrieved user by username: {username}")
            return user
        except UserModel.DoesNotExist:
            logger.warning(f"User with username {username} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by username {username}: {e}")
            raise
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        
        Args:
            email: Email address to look up
            
        Returns:
            User instance if found, None otherwise
        """
        if not email:
            return None
        
        try:
            user = UserModel.objects.get(email=email)
            logger.debug(f"Retrieved user by email: {email}")
            return user
        except UserModel.DoesNotExist:
            logger.warning(f"User with email {email} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by email {email}: {e}")
            raise
    
    @staticmethod
    def get_user_by_stripe_customer_id(
        stripe_customer_id: str,
        select_for_update: bool = False
    ) -> Optional[User]:
        """
        Retrieve a user by their Stripe customer ID.
        
        Args:
            stripe_customer_id: Stripe customer ID to look up
            select_for_update: If True, locks the row for update (for transactions)
            
        Returns:
            User instance if found, None otherwise
        """
        if not stripe_customer_id:
            return None
        
        try:
            queryset = UserModel.objects.filter(stripe_customer_id=stripe_customer_id)
            if select_for_update:
                queryset = queryset.select_for_update()
            user = queryset.get()
            logger.debug(f"Retrieved user by Stripe customer ID: {stripe_customer_id}")
            return user
        except UserModel.DoesNotExist:
            logger.warning(f"User with Stripe customer ID {stripe_customer_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by Stripe customer ID {stripe_customer_id}: {e}")
            raise
    
    @staticmethod
    def serialize_user(user: User) -> Dict:
        """
        Serialize a user instance to a dictionary.
        
        Args:
            user: User instance to serialize
            
        Returns:
            Dictionary containing serialized user data
            
        Raises:
            ValueError: If user is None
        """
        if user is None:
            raise ValueError("User cannot be None")
        
        serializer = UserSerializer(user)
        return serializer.data
    
    @staticmethod
    def refresh_user_from_db(user: User) -> User:
        """
        Refresh a user instance from the database.
        
        Args:
            user: User instance to refresh
            
        Returns:
            Refreshed User instance
            
        Raises:
            ValueError: If user is None or has no primary key
        """
        if user is None:
            raise ValueError("User cannot be None")
        
        if not user.pk:
            raise ValueError("User must have a primary key to refresh")
        
        user.refresh_from_db()
        logger.debug(f"Refreshed user {user.username} from database")
        return user

