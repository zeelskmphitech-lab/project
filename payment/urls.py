from django.urls import path,include
from .views import CartCreateView, CartItemUpdateDeleteView,BuyView,CheckoutView, CartItemView, AddressView

urlpatterns = [
    path('cart/',CartCreateView.as_view()),
    path('cart-item/',CartItemView.as_view()),
    path('cart-item/<int:pk>/',CartItemUpdateDeleteView.as_view()),
    path('buy/',BuyView.as_view()),  
    path('checkout/', CheckoutView.as_view()),
    path('address/', AddressView.as_view()), 
]