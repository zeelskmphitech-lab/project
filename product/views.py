from django.shortcuts import render
from .models import Products
from rest_framework.views import APIView
from .serializers import ProductSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

class ProductView(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = ProductSerializer
 
    def get_queryset(self):
        return Products.objects.filter(user=self.request.user,is_deleted=False)
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_seller:
            serializer.save(user=user)
        else:
            raise PermissionDenied("Buyer cannot create products")
        
class ProductUpdate(generics.UpdateAPIView,generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Products.objects.all()
    
    def get_queryset(self):
        return Products.objects.filter(user=self.request.user)
    def perform_update(self, serializer):
        instance = serializer.save(user=self.request.user)
        print("Product Updated:")
        print("ID:", instance.id)
        print("Name:", instance.name)
        print("Price:", instance.price)
        
class ProductDelete(generics.DestroyAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Products.objects.all()
    
    def get_queryset(self):
        return Products.objects.filter(user=self.request.user)
    
    def get(self, request, *args, **kwargs):
        return Response({"Message": "Use DELETE method"})
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        
class ProductRecover(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        product = Products.objects.get(pk=pk, user=request.user)

        product.is_deleted = False
        product.save()

        return Response({"message": "Recovered successfully"})