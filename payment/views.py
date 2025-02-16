from django.shortcuts import render , redirect

from django.contrib.auth.decorators import login_required

from .models import ShippingAddress , Order , OrderItem

from payment.forms import ShippingAddressForm

from cart.cart import Cart

from django.urls import reverse

from django.conf import settings

import stripe


from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version =settings.STRIPE_API_VERSION

@login_required(login_url='account:login')
def shipping(request):

    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)

    except ShippingAddress.DoesNotExist:

        shipping_address = None

    form = ShippingAddressForm(isinstance=shipping_address)

    if request.method == ' POST':

        form = ShippingAddressForm(request.POST, isinstance=shipping_address)

        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            return redirect('account:dashboard')
    return render(request, 'shipping/shipping.html', {'form': form})

def checkout(request):

    if request.user.is_authenticated:

        shipping_address, _ =ShippingAddress.objects.get_or_create(user=request.user) 
        
        return render(

            request, 'payment/checkout.html', {'shipping_address': shipping_address}
        )
    return render(request, 'payment/checkout.html')

def complete_order(request):
    
    if request.method == 'POST':

        payment_type = request.POST.get('stripe-payment')

        name = request.POST.get('name')

        email = request.POST.get('email')
        
        street_address = request.POST.get('street_address')
        
        apartment_address = request.POST.get('apartment_address')
        
        country = request.POST.get('country')
        
        zip = request.POST.get('zip')
        
        cart = Cart(request)
        
        total_price = cart.get_total_price()

        shipping_address, _ = ShippingAddress.objects.get_or_create(

            user= request.user,

            defaults={

                'name': name , 
                
                'email': email,

                'street_address': street_address,

                'apartment_address': apartment_address,

                'country': country,

                'zip': zip,

            },
        )
        if payment_type == 'stripe-payment':
            session_data = {

                'mode':'payment',
                
                'success_url':request.build_absolute_uri(
                
                    reverse('payment:payment-success')
                
                ),
                
                'cancel_url':request.build_absolute_uri(
                
                    reverse('payment:payment-failed')
                
                ),
                
                'line_item': [],
            }

            if request.user.is_authenticated:
                
                order = Order.objects.create(
                
                    user = request.user,
                
                    shipping_address = shipping_address,
                
                    amount=total_price,
                )

                for item in cart:

                    OrderItem.objects.create(

                        order=order,

                        product=item['product'],

                        price=item['price'],

                        quantity=item['qty'],

                        user=request.user,
                    
                    )

                    session_data['line_items'].append(
                        
                        {
                            'price_data':{
                                'unit_amount': int(item['price']* Decimal(100)),
                                'currency':'usd',
                                'product_data':{'name':item['product']},
                            },
                            'quantity':item['qty'],
                        }
                    )
                session_data['client_reference_id'] = order.id
                session = stripe.checkout.Session.create(**session_data)
                return redirect(session.url, code=303)
            
            else:
                 order = Order.objects.create(
                
               
                
                    shipping_address = shipping_address,
                
                    amount=total_price,
                )

            for item in cart:

                    OrderItem.objects.create(

                        order=order,

                        product=item['product'],

                        price=item['price'],

                        quantity=item['qty'],


                    
                    )

                    session_data['line_items'].append(
                        
                        {
                            'price_data':{
                                'unit_amount': int(item['price']* Decimal(100)),
                                'currency':'usd',
                                'product_data':{'name':item['product']},
                            },
                            'quantity':item['qty'],
                        }
                    )
                    session_data['client_reference_id'] = order.id
                    session = stripe.checkout.Session.create(**session_data)
                    return redirect(session.url, code=303)

def payment_success(request):

    for key in list (request.session.keys()):

        if key == 'session_key':

            del request.session[key]

    return render(request, 'payment/payment-success.html')

def payment_failed(request):

    return render(request, 'payment/payment-failed.html')


