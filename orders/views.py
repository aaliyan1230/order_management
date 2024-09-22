from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser

from .models import Order
from .serializers import OrderSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})


class AllUserEmailsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        emails = CustomUser.objects.values_list("email", flat=True)
        return Response({"emails": list(emails)})


class OrdersByEmailView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        emails = request.data.get("emails", [])
        if not emails:
            return Response({"error": "No email addresses provided"}, status=400)

        users = CustomUser.objects.filter(email__in=emails)
        orders = Order.objects.filter(user__in=users)
        serializer = OrderSerializer(orders, many=True)

        return Response(
            {
                "orders": serializer.data,
                "total_orders": orders.count(),
                "emails_found": list(users.values_list("email", flat=True)),
            }
        )
