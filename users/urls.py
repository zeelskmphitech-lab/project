from django.urls import path,include
from .views import RegisterView,LoginView,LogoutView,RefreshView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
    path("api-auth/", include("rest_framework.urls")),
    path('token/refresh/', RefreshView.as_view()),
    path('logout/',LogoutView.as_view()),
]