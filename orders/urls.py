from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AllUserEmailsView,
    CustomAuthToken,
    OrdersByEmailView,
    OrderViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    path("api-token-auth/", CustomAuthToken.as_view(), name="api_token_auth"),
    path("all-user-emails/", AllUserEmailsView.as_view(), name="all_user_emails"),
    path("orders-by-email/", OrdersByEmailView.as_view(), name="orders_by_email"),
]
