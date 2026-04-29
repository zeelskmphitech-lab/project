from django.urls import path
from .views import ProductView,ProductUpdate,ProductDelete,ProductRecover

urlpatterns = [
    path('products/',ProductView.as_view()),
    path('products/<int:pk>/',ProductUpdate.as_view()),
    path('products/delete/<int:pk>/',ProductDelete.as_view()),
    path('products/recover/<int:pk>/',ProductRecover.as_view()),
]