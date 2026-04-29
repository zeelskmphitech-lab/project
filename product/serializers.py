from rest_framework import serializers
from .models import Products

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Products
        fields = ['id','user','product_name','product_type','company_name','section','description','price','stoke']
        read_only_fields = ['user']