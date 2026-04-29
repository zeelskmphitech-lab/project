from django.db import models
from users.models import Users
from product.models import Products
from django.utils import timezone
from product.models import Products

class Cart(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
class Buy(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    coupon_code = models.CharField(max_length=50, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        default="pending"
    )
    payment_method = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Checkout(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    phoneno = models.BigIntegerField()
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    def __str__(self):
        return f"{self.user}"
    
class CheckoutItem(models.Model):
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
class Address(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.IntegerField()
    
class CouponCode(models.Model):
    DISCOUNT_TYPE_CHOICE ={
                        "Fixed Amount Discounts":"Fixed Amount Discounts",
                        "Percentage Discounts (With Caps)":"Percentage Discounts (With Caps)",
                        "BOGO":"BOGO",
                        "Minimum Spend Coupons (Thresholds)":"Minimum Spend Coupons (Thresholds)",
                        "Category-Specific Discounts":"Category-Specific Discounts",
                        "First-Purchase / New User Coupons":"First-Purchase / New User Coupons"
    }
    
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True,default="Null")
    make_coupon_code = models.CharField(blank=False,null=False,default="Not Available")
    discount_type = models.CharField(blank=False,null=False,default="No Discount",choices=DISCOUNT_TYPE_CHOICE)
    