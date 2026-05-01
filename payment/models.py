from django.db import models
from users.models import Users
from product.models import Products
from django.utils import timezone
from product.models import Products
from django.core.exceptions import ValidationError

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
    
class Checkout(models.Model):
    
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    phoneno = models.BigIntegerField()
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)  
    def __str__(self):
        return f"{self.user}"
    # purchased = models.BooleanField(default=False)
    
class CheckoutItem(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE)
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    coupon_code = models.CharField(max_length=50, null=True, blank=True)
    
class Address(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE,unique=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.IntegerField()
    have_address = models.BooleanField(default=False)
    
class CouponCode(models.Model):
    DISCOUNT_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    TYPE_CHOICES = (
        ('all',"Discount On Total Cart"),
        ('product',"Discount On Specific Product")
    )
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True,default="Null")
    make_coupon_code = models.CharField(blank=False,null=False,default="all")
    discount_choice = models.CharField(blank=False,null=False,default="No Discount",choices=TYPE_CHOICES)
    discount_type = models.CharField(blank=False,null=False,default="No Discount",choices=DISCOUNT_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    
    def clean(self):
        if self.discount_choice == 'all':
            if self.discount_type == 'percentage' and self.value > 100:
                raise ValidationError("Percentage discount cannot be more than 100%.")
            
            if self.discount_type == 'percentage' and not self.max_discount_limit:
                raise ValidationError("Please provide a Maximum Discount Limit for percentage coupons.")
        

    def is_valid(self, cart_total):
        now = timezone.localtime()
        if not self.active:
            return False
        if not (self.valid_from <= now <= self.valid_to):
            return False
        if cart_total < self.min_purchase_amount:
            return False
        return True

    def all_calculate_discount(self, cart_total):
        if self.discount_choice == 'all':
            if self.discount_type == 'percentage':
                discount = (cart_total * self.value) / 100
                if self.max_discount_limit:
                    discount = min(discount, self.max_discount_limit)
            else:
                discount = self.value
            
            return min(discount, cart_total)
        
    def product_calculate_discount(self,product_total):
        if self.discount_choice == 'product':
            if self.discount_type == 'percentage':
                discount = (product_total * self.value) / 100
                if self.max_discount_limit:
                    discount = min(discount, self.max_discount_limit)
            else:
                discount = self.value
            
            return min(discount, product_total)
    
class Reviews(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    checkoutitem = models.ForeignKey(CheckoutItem,on_delete=models.CASCADE)
    review = models.TextField()
    
class Purchase(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('card', 'Card'),
        ('upi', 'UPI'),
    )
    user=models.ForeignKey(Users,on_delete=models.CASCADE)
    checkoutitem = models.ForeignKey(CheckoutItem,on_delete=models.CASCADE)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=False,
        blank=False
    )
    purchased_at = models.DateTimeField(auto_now_add=True)
    has_purchased = models.BooleanField(default=False)
    card_number = models.IntegerField(null=True,blank=True)