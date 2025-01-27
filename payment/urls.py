from django.urls import path , include

from . import views

from django_email_verification import urls as email_urls

urlpatterns = [

    path('payment-sucess/', views.payment_success, name='payment-success'),

    path('payment-failed/', views.payment_failed, name='payment-failed'),

    path('shipping/', views.shipping, name='shipping'),

    path('checkout/', views.checkout, name='checkout'),

    path('complete-order/', views.complete_order, name='complete_order'),
]