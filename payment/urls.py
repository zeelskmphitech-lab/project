from django.urls import path,include
from .views import CartCreateView, CartItemUpdateDeleteView,CheckoutView, CartItemView, AddressView,CouponCodeCreateView,ReviewsView,MyOrdersView,PurchaseView

urlpatterns = [
    path('cart/',CartCreateView.as_view()),
    path('cart-item/',CartItemView.as_view()),
    path('cart-item/<int:pk>/',CartItemUpdateDeleteView.as_view()),
    path('checkout/', CheckoutView.as_view()),
    path('address/', AddressView.as_view()), 
    path('create-coupon/', CouponCodeCreateView.as_view()),   
    path('review/<int:checkoutitem_id>/', ReviewsView.as_view()),   
    path('my-orders/', MyOrdersView.as_view()),
    path('purchase/<int:checkout_id>/',PurchaseView.as_view(),name="purchase"),
]