from django.test import TestCase, Client, RequestFactory
import json
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from shop.models import ProductProxy, Category

from .views import cart_view, cart_add, cart_update, cart_delete


class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory().get(reverse("cart:cart-view"))
        self.middleware = SessionMiddleware(self.factory)
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_view(self):
        request = self.factory
        response = cart_view(request)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(
            self.client.get(reverse("cart:cart-view")), "cart/cart-view.html"
        )


class CartAddViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Category_1")
        self.product = ProductProxy.objects.create(
            title="Example Product", price=10.0, category=self.category
        )
        self.factory = RequestFactory().post(
            reverse("cart:add-to-cart"),
            {"action": "post", "product_id": self.product.id, "product_qty": 2},
        )
        self.middleware = SessionMiddleware(self.factory)
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_add(self):
        request = self.factory
        response = cart_add(request)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["product"], "Example Product")
        self.assertEqual(data["qty"], 2)


class CartDeleteViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Category 1")
        self.product = ProductProxy.objects.create(
            title="Example_Product", price=10.0, category=self.category
        )
        self.factory = RequestFactory().post(
            reverse("cart:delete-to-cart"),
            {"action": "post", "product_id": self.product.id},
        )
        self.middleware = SessionMiddleware(self.factory)
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_delete(self):
        request = self.factory
        response = cart_delete(request)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["qty"], 0)


class CartUpdateViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Category 1")
        self.product = ProductProxy.objects.create(
            title="Example_Product", price=10.0, category=self.category
        )
        self.factory = RequestFactory().post(
            reverse("cart:add-to-cart"),
            {"action": "post", "product_id": self.product.id, "product_qty": 2},
        )
        self.factory = RequestFactory().post(
            reverse("cart:update-to-cart"),
            {"action": "post", "product_id": self.product.id, "product_qty": 5},
        )
        self.middleware = SessionMiddleware(self.factory)
        self.middleware.process_request(self.factory)
        self.factory.session.save()

    def test_cart_update(self):
        request = self.factory
        response = cart_add(request)
        response = cart_update(request)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["total"], "50.00")
        self.assertEqual(data["qty"], 5)
