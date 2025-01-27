from django.contrib import admin
from django.urls import path
from .views import product_view, product_detail_view, category_list

app_name = "shop"

urlpatterns = [
    path("", product_view, name="products"),
    path("<slug:slug>/", product_detail_view, name="product-detail"),
    path("search/<slug:slug>/", category_list, name="category-list"),
]

# shop:products
# shop:product-detail
# shop:category-list
