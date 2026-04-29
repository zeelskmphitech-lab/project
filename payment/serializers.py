from rest_framework import serializers
from .models import Cart,Buy,Checkout,CartItem,Address

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]
              
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ["id", "created_at", "items"]
        
class BuySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Buy
        fields = ['id','product','product_name','quantity','price','discount','final_price','coupon_code','payment_status', 'created_at']
        
class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = ["id", 'phoneno',"coupon_code","created_at"]
        read_only_fields = ["id", "created_at"]
        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country', 'state', 'city', 'pincode']