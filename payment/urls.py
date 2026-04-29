from django.urls import path,include
from .views import CartCreateView, CartItemUpdateDeleteView,BuyView,CheckoutView, CartItemView, AddressView,CouponCodeCreateView,ReviewsView

urlpatterns = [
    path('cart/',CartCreateView.as_view()),
    path('cart-item/',CartItemView.as_view()),
    path('cart-item/<int:pk>/',CartItemUpdateDeleteView.as_view()),
    path('buy/',BuyView.as_view()),  
    path('checkout/', CheckoutView.as_view()),
    path('address/', AddressView.as_view()), 
    path('create-coupon/', CouponCodeCreateView.as_view()),   
    path('review/', ReviewsView.as_view()),   
]