from django.contrib import admin
from .models import Users

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('email','username', 'first_name', 'last_name','is_seller')
    list_filter = ('is_seller',)