from django.contrib import admin
from .models import Cart,Buy,Checkout,CartItem,CheckoutItem,Address


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id','user','created_at','is_active')
    list_filter = ('created_at','is_active')
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('get_user','product','quantity')
    list_filter = ('quantity',)
    def get_user(self, obj):
        return obj.cart.user
    get_user.short_description = 'User'
    
@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ('id','user','phoneno','created_at','coupon_code')
    list_filter = ('created_at',)

@admin.register(Buy)
class Buy(admin.ModelAdmin):
    list_display =('user','product','quantity','price','final_price','discount','created_at')
    list_filter = ('created_at','product','quantity')
    
@admin.register(CheckoutItem)
class CheckoutItemAdmin(admin.ModelAdmin):
    list_display = ('checkout','product','quantity','price')
    list_filter = ('price','checkout')
    
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('country','state','city','pincode')
    list_filter = ('country','state','city')