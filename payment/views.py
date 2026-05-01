from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from product.models import Products
from .models import Cart , Checkout , CartItem , Address , CouponCode,Reviews,CheckoutItem,Purchase
from .serializers import CartSerializer,CheckoutSerializer,CartItemSerializer,AddressSerializer , CouponCodeSerializer,ReviewsSerializer,CheckoutItemSerializer,PurchaseSerializer
from django.db import transaction
from .permissions import IsSeller
from decimal import Decimal
from django.shortcuts import get_object_or_404

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
        
        with transaction.atomic():

            checkout = serializer.save(user=user, cart=cart)

            items = cart.items.all()

            total = Decimal("0")
            discount = Decimal("0")

            code = (checkout.coupon_code or "").strip()
            coupon = None

            if code:
                coupon = CouponCode.objects.filter(
                    make_coupon_code__iexact=code,
                    active=True
                ).first()

                if not coupon:
                    return Response({"error": "Invalid coupon code"}, status=400)

            for item in items:
                item_total = item.product.price * item.quantity
                total += item_total

                item_discount = Decimal("0")

                if coupon:
                    if coupon.discount_choice == 'all':
                        item_discount = coupon.all_calculate_discount(item_total)

                    elif coupon.discount_choice == 'product':
                        if item.product == coupon.product:
                            item_discount = coupon.product_calculate_discount(item_total)

                discount += item_discount

                final_price = item_total - item_discount

                CheckoutItem.objects.create(
                    checkout=checkout,
                    user=user,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    discount=item_discount,
                    final_price=final_price,
                    coupon_code=checkout.coupon_code,
                )

            if coupon and not coupon.is_valid(total):
                return Response({"error": "Coupon not valid"}, status=400)

            final_total = total - discount

            checkout.total_amount = final_total
            checkout.discount_amount = discount
            checkout.save()

            cart.is_active = False
            cart.save()
            items.delete()
            
        return Response({
            "message": "Checkout successful",
            "checkout_id": checkout.id,
            "items": serializer.data,
            "cart_total": final_total,
            "discount":discount
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
        serializer.save(user=self.request.user,have_address = True)
        
class CouponCodeCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsSeller]
    serializer_class = CouponCodeSerializer
    
    def get_queryset(self):
        return CouponCode.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class MyOrdersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    def get_queryset(self):
        return Checkout.objects.filter(user=self.request.user)
        
class ReviewsView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewsSerializer

    def perform_create(self, serializer):
        user = self.request.user
        checkoutitem_id = self.kwargs.get("checkoutitem_id")

        checkoutitem = get_object_or_404(
            CheckoutItem,
            id=checkoutitem_id,
            checkout__user=user
        )

        if Reviews.objects.filter(user=user, checkoutitem=checkoutitem).exists():
            raise serializers.ValidationError("You already reviewed this product")

        serializer.save(
            user=user,
            product=checkoutitem.product,
            checkoutitem=checkoutitem
        )
        
class PurchaseView(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = PurchaseSerializer
    
    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)
        
    def create(self,request,*args,**kwargs):
        user= request.user
        checkout_id = self.kwargs.get('checkout_id')
        
        has_address = Address.objects.filter(
            user=self.request.user,
        ).exists()
        
        if not has_address:
            raise serializers.ValidationError({
                "massage":"Please Assign Address First."
            })
        
        checkout = Checkout.objects.filter(id=checkout_id, user=user).first()
        
        if not checkout:
            return Response({"error": "Checkout record not found."}, status=404)
        
        items = CheckoutItem.objects.filter(checkout=checkout)
        
        if not items.exists():
            return Response({"error": "No items in checkout"}, status=400)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_method = serializer.validated_data.get("payment_method")
        
        already_purchased = Purchase.objects.filter(user=user,checkoutitem__in=items,has_purchased=True).exists()
        
        if already_purchased:
            return Response({"error":"Already purchased this product."},status=400)
        
        elif not already_purchased:
            if payment_method == 'cod':
                data = []
                for item in items:
                    Purchase.objects.create(
                        user=user,
                        checkoutitem=item,
                        payment_method='cod',
                        payment_status='pending',
                        has_purchased=True
                    )    
                    data.append({
                        "product": item.product.product_name,
                        "price": item.final_price
                    })
                return Response(
                    {
                        "Items":data,
                        "message":"Product Will Deliver soon."
                        })
                
            elif payment_method == 'card':
                serializer = PurchaseSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                card_holder_name=serializer.validated_data.get('card_holder_name')
                card_number=serializer.validated_data.get('card_number')
                card_expiration_date=serializer.validated_data.get('card_expiration_date')
                card_security_code=serializer.validated_data.get('card_security_code')                
                
                for item in items:
                    Purchase.objects.create(
                        user=user,
                        checkoutitem=item,
                        payment_method='card',
                        payment_status='paid',
                        has_purchased=True,
                        card_holder_name=card_holder_name,
                        card_number=card_number,
                        card_expiration_date=card_expiration_date,
                        card_security_code=card_security_code                        
                    ) 
                return Response({"message":"Payment Successful."})
            
            elif payment_method == 'upi':
                serializer = PurchaseSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                upi_id = serializer.validated_data.get('upi_id')
                upi_pin = serializer.validated_data.get('upi_pin')
                
                for item in items:
                    Purchase.objects.create(
                        user=user,
                        checkoutitem=item,
                        payment_method='upi',
                        payment_status='paid',
                        has_purchased=True,
                        upi_id=upi_id,
                        upi_pin=upi_pin
                    ) 
                return Response({"message":"Payment Successful."})