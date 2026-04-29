from django.contrib import admin
from .models import Products

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','user','product_name','product_type','company_name','section','description','price','stoke')