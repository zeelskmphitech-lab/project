from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .models import Cart , Buy , Checkout , CartItem , CheckoutItem , Address , CouponCode
from .serializers import CartSerializer,BuySerializer,CheckoutSerializer,CartItemSerializer,AddressSerializer , CouponCodeSerializer
from django.db import transaction
from decimal import Decimal

class CartCreateView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
class CartItemView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user,
            cart__is_active=True
        )   

    def perform_create(self, serializer):
        quantity = serializer.validated_data.get("quantity", 1)

        if quantity <= 0:
            raise serializers.ValidationError({
                "message": "Quantity must be greater than 0"
            })

        cart, _ = Cart.objects.get_or_create(
            user=self.request.user,
            is_active=True
        )
        cart_item = CartItem.objects.filter(cart=cart, product=serializer.validated_data['product']).first()

        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            serializer.save(cart=cart)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        total = sum(item.product.price * item.quantity for item in queryset)

        return Response({
            "items": serializer.data,
            "cart_total": total
        })
        
class CartItemUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_update(self, serializer):
        quantity = serializer.validated_data.get("quantity")

        if quantity <= 0:
            serializer.instance.delete()
        else:
            serializer.save()
        
class BuyView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BuySerializer

    def get_queryset(self):
        return Buy.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class CheckoutView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    def create(self, request, *args, **kwargs):
        user = request.user     

        cart = Cart.objects.filter(user=user, is_active=True).first()
        if not cart:
            return Response({"message": "No active cart"}, status=400)

        items = cart.items.all()
        if not items.exists():
            return Response({"message": "Cart is empty"}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        checkout = serializer.save(user=user, cart=cart)

        total = 0
        discount = 0

        code = (checkout.coupon_code or "").strip().upper()

        for item in items:
            item_total = item.product.price * item.quantity
            item_discount = 0

            code = (checkout.coupon_code or "").strip().upper()

            
            if code == "SAVE20":
                item_discount = item_total * Decimal("0.20")

            elif code == "SAVE30":
                item_discount = item_total * Decimal("0.30")

            elif code == "SAVE100":
                item_discount = item_total

            elif code == "BOAT50" and item.product.id == 7:
                item_discount = item_total * Decimal("0.50")

            final_price = item_total - item_discount

            Buy.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                discount=item_discount,
                final_price=final_price,
                coupon_code=checkout.coupon_code,
                payment_status="pending"
            )

        cart.is_active = False
        cart.save()

        cart.items.all().delete()

        return Response({
            "message": "Checkout successful",
            "checkout_id": checkout.id
        }, status=status.HTTP_201_CREATED)
        
class AddressView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    
    def perform_create(self, serializer):
        cart = Cart.objects.filter(
            user=self.request.user,
            is_active=True
        ).first()

        if cart:
            raise serializers.ValidationError({
                "message": "Complete checkout before adding address."
            })

        serializer.save(user=self.request.user)
        
class CouponCodeCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CouponCodeSerializer
    
    def get_queryset(self):
        return CouponCode.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save()