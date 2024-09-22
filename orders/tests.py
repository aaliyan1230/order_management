from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Order


class AllUserEmailsViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = User.objects.create_superuser(
            "admin", "admin@example.com", "adminpass"
        )
        self.regular_user = User.objects.create_user(
            "user", "user@example.com", "userpass"
        )

    def test_superuser_can_access(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get("/api/all-user-emails/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("emails", response.data)
        self.assertIn("admin@example.com", response.data["emails"])
        self.assertIn("user@example.com", response.data["emails"])

    def test_regular_user_cannot_access(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/all-user-emails/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get("/api/all-user-emails/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrdersByEmailViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = User.objects.create_superuser(
            "admin", "admin@example.com", "adminpass"
        )
        self.user1 = User.objects.create_user("user1", "user1@example.com", "userpass")
        self.user2 = User.objects.create_user("user2", "user2@example.com", "userpass")

        Order.objects.create(user=self.user1, order_number="ORD001", total_amount=100)
        Order.objects.create(user=self.user1, order_number="ORD002", total_amount=200)
        Order.objects.create(user=self.user2, order_number="ORD003", total_amount=300)

    def test_superuser_can_access(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            "/api/orders-by-email/",
            {"emails": ["user1@example.com", "user2@example.com"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["orders"]), 3)
        self.assertEqual(response.data["total_orders"], 3)
        self.assertCountEqual(
            response.data["emails_found"], ["user1@example.com", "user2@example.com"]
        )

    def test_regular_user_cannot_access(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/orders-by-email/", {"emails": ["user1@example.com"]}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access(self):
        response = self.client.post(
            "/api/orders-by-email/", {"emails": ["user1@example.com"]}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_emails_provided(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post("/api/orders-by-email/", {"emails": []})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_existent_email(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(
            "/api/orders-by-email/", {"emails": ["nonexistent@example.com"]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["orders"]), 0)
        self.assertEqual(response.data["total_orders"], 0)
        self.assertEqual(response.data["emails_found"], [])


class UserViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.superuser = User.objects.create_superuser(
            "admin", "admin@example.com", "adminpass"
        )
        self.regular_user = User.objects.create_user(
            "user", "user@example.com", "userpass"
        )

    def test_list_users_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # superuser and regular user

    def test_list_users_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 2
        )  # regular users can see the list, but not modify

    def test_create_user_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass",
        }
        response = self.client.post("/api/users/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_create_user_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass",
        }
        response = self.client.post("/api/users/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_superuser(self):
        self.client.force_authenticate(user=self.superuser)
        data = {"email": "updated@example.com"}
        response = self.client.patch(f"/api/users/{self.regular_user.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, "updated@example.com")

    def test_update_user_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {"email": "updated@example.com"}
        response = self.client.patch(f"/api/users/{self.regular_user.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrderViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user("user1", "user1@example.com", "userpass")
        self.user2 = User.objects.create_user("user2", "user2@example.com", "userpass")
        self.order1 = Order.objects.create(
            user=self.user1, order_number="ORD001", total_amount=100
        )
        self.order2 = Order.objects.create(
            user=self.user2, order_number="ORD002", total_amount=200
        )

    def test_list_orders(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # user1 should only see their own order
        self.assertEqual(response.data[0]["order_number"], "ORD001")

    def test_create_order(self):
        self.client.force_authenticate(user=self.user1)
        data = {"order_number": "ORD003", "total_amount": 300}
        response = self.client.post("/api/orders/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 3)
        self.assertEqual(Order.objects.get(order_number="ORD003").user, self.user1)

    def test_retrieve_own_order(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/orders/{self.order1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_number"], "ORD001")

    def test_retrieve_other_user_order(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/orders/{self.order2.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_own_order(self):
        self.client.force_authenticate(user=self.user1)
        data = {"total_amount": 150}
        response = self.client.patch(f"/api/orders/{self.order1.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.total_amount, 150)

    def test_update_other_user_order(self):
        self.client.force_authenticate(user=self.user1)
        data = {"total_amount": 250}
        response = self.client.patch(f"/api/orders/{self.order2.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_order(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f"/api/orders/{self.order1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 1)

    def test_delete_other_user_order(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f"/api/orders/{self.order2.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Order.objects.count(), 2)
