from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'subscription_status', 'current_plan', 'total_amount_paid', 'stripe_customer_id')
    list_filter = ('subscription_status', 'current_plan')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Subscription Info', {
            'fields': ('subscription_status', 'current_plan', 'total_amount_paid', 'stripe_customer_id', 'stripe_subscription_id')
        }),
    )

