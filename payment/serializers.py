from rest_framework import serializers
from .models import Cart,CheckoutItem,Checkout,CartItem,Address,CouponCode,Reviews

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]
              
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ["id", "created_at", "items"]
    
        
class CheckoutSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Checkout
        fields = ["id", 'phoneno',"coupon_code","created_at",'items','payment_method','payment_status']
        read_only_fields = ["id", "created_at"]
        
class CheckoutItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = CheckoutItem
        fields = ['id','product','product_name','quantity','price','discount','final_price','coupon_code']
        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country', 'state', 'city', 'pincode']
 
class CouponCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponCode
        fields = ['id','product','make_coupon_code','discount_choice','discount_type','value','min_purchase_amount','max_discount_limit','valid_from','valid_to','active']    
        read_only_fields = ['user']

    def validate_product(self, product):
        user = self.context['request'].user

        if product.user != user:
            raise serializers.ValidationError("You can only create coupon for your own product")

        return product
    
class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['id','product','review']