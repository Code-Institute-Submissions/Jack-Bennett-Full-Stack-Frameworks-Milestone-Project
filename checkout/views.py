from django.shortcuts import render, get_object_or_404, reverse, \
    redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MakePaymentForm, OrderForm
from .models import OrderLineItem, Order
from django.conf import settings
from django.utils import timezone
from products.models import Product
from accounts.models import Customer
import stripe

stripe.api_key = settings.STRIPE_SECRET


@login_required
def checkout(request):
    """
    Returns the checkout page and allows the
    user to enter the personal and payment
    details in order to complete their order
    """

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        payment_form = MakePaymentForm(request.POST)

        if order_form.is_valid() and payment_form.is_valid():
            order = order_form.save(commit=False)
            order.date = timezone.now()
            customer = Customer.objects.get(user=request.user)
            order.customer = customer
            order.save()

            cart = request.session.get('cart', {})
            total = 0
            for (id, quantity) in cart.items():
                product = get_object_or_404(Product, pk=id)
                total += quantity * product.price
                order_line_item = OrderLineItem(order=order,
                                                product=product,
                                                quantity=quantity)
                order_line_item.save()

            try:
                customer = stripe.Charge.create(amount=int(total
                                                * 100), currency='GBP',
                                                description=request.user.email,
                                                card=payment_form.cleaned_data['stripe_id'])
            except stripe.error.CardError:
                messages.error(request, 'Your card was declined!')

            if customer.paid:
                messages.success(request, 'You have successfully paid')
                request.session['cart'] = {}
                return redirect(reverse('products'))
            else:
                messages.error(request, 'Unable to take payment')
        else:
            print(payment_form.errors)
            messages.error(request,
                           'We were unable to take a payment with that card!'
                           )
    else:
        payment_form = MakePaymentForm()
        order_form = OrderForm()

    return render(request, 'checkout.html', {'order_form': order_form,
                  'payment_form': payment_form,
                  'publishable': settings.STRIPE_PUBLISHABLE})


@login_required
def delete_order(request, pk):
    """Cancel an order from the profile page"""

    order = Order.objects.get(id=pk)
    order.delete()
    return redirect('profile_no_orders')
