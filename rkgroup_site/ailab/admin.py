from django.contrib import admin

from .models import PhoneVerificationCode


@admin.register(PhoneVerificationCode)
class PhoneVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ['phone', 'is_used', 'attempts', 'created_at', 'expires_at']
    list_filter = ['is_used']
    search_fields = ['phone']
    readonly_fields = ['phone', 'code', 'attempts', 'is_used', 'created_at', 'expires_at']

    def has_add_permission(self, request):
        return False
