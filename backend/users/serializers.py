"""
Serializers for user and subscription data.
"""
from rest_framework import serializers
from typing import Literal
from .models import User
from .constants import PLAN_BASIC, PLAN_PRO, PLAN_NONE


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Includes computed lifetime_value field for easy frontend consumption.
    """
    lifetime_value = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'subscription_status',
            'current_plan',
            'total_amount_paid',
            'lifetime_value',
        ]
        read_only_fields = ['id', 'total_amount_paid']
    
    def get_lifetime_value(self, obj: User) -> float:
        """
        Return lifetime value formatted as dollars.
        
        Args:
            obj: User instance
            
        Returns:
            float: Lifetime value in dollars
        """
        return obj.get_lifetime_value_dollars()


class SubscriptionUpdateSerializer(serializers.Serializer):
    """
    Serializer for subscription update requests.
    
    Validates plan selection for upgrade/downgrade/cancel operations.
    """
    plan = serializers.ChoiceField(
        choices=[PLAN_BASIC, PLAN_PRO, PLAN_NONE],
        help_text="Target plan: 'basic', 'pro', or 'none' (cancel)"
    )
    
    def validate_plan(self, value: str) -> str:
        """
        Validate plan value.
        
        Args:
            value: Plan string value
            
        Returns:
            str: Validated plan value
            
        Raises:
            serializers.ValidationError: If plan is invalid
        """
        valid_plans = [PLAN_BASIC, PLAN_PRO, PLAN_NONE]
        if value not in valid_plans:
            raise serializers.ValidationError(
                f"Plan must be one of: {', '.join(valid_plans)}"
            )
        return value

