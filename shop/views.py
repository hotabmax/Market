from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.debug import sensitive_post_parameters
from django.utils import timezone
from .models import Category, Product, Order, OrderItem
from .forms import OrderCreateForm, OrderEmailForm, ProductSearchForm
import logging

logger = logging.getLogger('shop')


def home(request):
    """Главная страница"""
    categories = Category.objects.filter(active=True)[:6]
    featured_products = Product.objects.filter(
        available=True, featured=True
    )[:8]
    new_products = Product.objects.filter(
        available=True
    ).order_by('-created_at')[:4]

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'new_products': new_products,
    }
    return render(request, 'shop/home.html', context)


def catalog(request, category_slug=None):
    """Каталог товаров"""
    categories = Category.objects.filter(active=True)
    search_form = ProductSearchForm(categories=categories)

    products = Product.objects.filter(available=True)

    # Фильтрация по категории
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, active=True)
        products = products.filter(category=category)
        search_form = ProductSearchForm(
            categories=categories,
            data=request.GET,
            initial={'category': category_slug}
        )
    else:
        category = None
        search_form = ProductSearchForm(
            categories=categories,
            data=request.GET
        )

    # Поиск
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        search_form = ProductSearchForm(
            categories=categories,
            data=request.GET
        )

    # Фильтр по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Сортировка
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category,
        'search_form': search_form,
        'sort_by': sort_by,
    }
    return render(request, 'shop/catalog.html', context)


def product_detail(request, product_slug):
    """Страница товара"""
    product = get_object_or_404(Product, slug=product_slug, available=True)
    similar_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'similar_products': similar_products,
    }
    return render(request, 'shop/product_detail.html', context)


def cart_detail(request):
    """Страница корзины"""
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for product_id_str, data in cart.items():
        product = get_object_or_404(Product, id=int(product_id_str))
        quantity = data['quantity']
        # ВАЖНО: цена берётся из БД, не из сессии
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': product.price * quantity,
        })
        total_price += product.price * quantity

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': sum(item['quantity'] for item in cart_items),
    }
    return render(request, 'shop/cart.html', context)


@require_POST
@sensitive_post_parameters()
def cart_add(request, product_slug):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, slug=product_slug)

    if not product.is_in_stock:
        messages.error(request, 'Товар отсутствует на складе')
        return redirect('shop:product_detail', product_slug=product_slug)

    cart = request.session.get('cart', {})
    product_id = str(product.id)

    if product_id in cart:
        cart[product_id]['quantity'] = min(
            cart[product_id]['quantity'] + 1,
            product.stock
        )
    else:
        cart[product_id] = {
            'quantity': 1,
            'price': str(product.price),
        }

    request.session['cart'] = cart
    messages.success(request, f'«{product.name}» добавлен в корзину')
    return redirect('shop:cart_detail')


@require_POST
def cart_remove(request, cart_item_id):
    """Удаление товара из корзины"""
    cart = request.session.get('cart', {})
    product_id = str(cart_item_id)

    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, 'Товар удалён из корзины')

    return redirect('shop:cart_detail')


@require_POST
def cart_update(request):
    """Обновление количества товаров в корзине"""
    cart = request.session.get('cart', {})

    for product_id_str, data in list(cart.items()):
        product = get_object_or_404(Product, id=int(product_id_str))
        new_quantity = request.POST.get(f'quantity_{product_id_str}', 1)

        try:
            new_quantity = int(new_quantity)
            if new_quantity <= 0:
                del cart[product_id_str]
            else:
                data['quantity'] = min(new_quantity, product.stock)
        except (ValueError, TypeError):
            pass

    request.session['cart'] = cart
    messages.success(request, 'Корзина обновлена')
    return redirect('shop:cart_detail')


def checkout(request):
    """Оформление заказа"""
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Корзина пуста')
        return redirect('shop:catalog')

    # ВАЖНО: проверяем наличие и актуальность цен из БД
    for product_id_str in cart.keys():
        product = get_object_or_404(Product, id=int(product_id_str))
        if not product.is_in_stock:
            messages.error(
                request,
                f'Товар «{product.name}» отсутствует на складе'
            )
            return redirect('shop:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save()
                total_price = 0

                for product_id_str, data in cart.items():
                    product = get_object_or_404(Product, id=int(product_id_str))
                    quantity = data['quantity']
                    # ВАЖНО: цена берётся из БД в момент заказа
                    price = product.price

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=quantity,
                        price=price,
                    )

                    # Уменьшаем остаток
                    product.stock -= quantity
                    if product.stock == 0:
                        product.stock_status = 'out_of_stock'
                    product.save()

                    total_price += price * quantity

                order.total_price = total_price
                order.save()

                # Очищаем корзину
                del request.session['cart']
                # Сохраняем email для отслеживания заказов
                request.session['order_email'] = order.email

            logger.info(
                f"Order #{order.id} created by {order.email}, "
                f"total: {total_price}"
            )

            messages.success(
                request,
                f'Заказ #{order.id} успешно оформлен! '
                f'Мы свяжемся с вами для подтверждения.'
            )
            return redirect('shop:order_detail', order_id=order.id)
    else:
        form = OrderCreateForm()

    # ВАЖНО: считаем итог из БД, не из сессии
    total_price = 0
    for pid, data in cart.items():
        product = Product.objects.get(id=int(pid))
        total_price += product.price * data['quantity']

    context = {
        'form': form,
        'total_price': total_price,
    }
    return render(request, 'shop/checkout.html', context)


def order_detail(request, order_id):
    """Страница заказа — только если email совпадает с сессией"""
    order = get_object_or_404(Order, id=order_id)

    # IDOR protection: проверяем что email в сессии совпадает с email заказа
    session_email = request.session.get('order_email', '')
    if session_email != order.email:
        messages.warning(
            request,
            'У вас нет доступа к этому заказу. Войдите, указав email из заказа.'
        )
        return redirect('shop:orders_list')

    # Сохраняем email для отслеживания заказов
    request.session['order_email'] = order.email
    context = {'order': order}
    return render(request, 'shop/order_detail.html', context)


def orders_list(request):
    """Список заказов пользователя (по email)"""
    email = request.session.get('order_email', '')
    orders = Order.objects.none()
    total_spent = 0

    if email:
        orders = Order.objects.filter(email=email).order_by('-created_at')
        total_spent = sum(o.total_price for o in orders)

    if request.method == 'POST':
        email_form = OrderEmailForm(request.POST)
        if email_form.is_valid():
            email = email_form.cleaned_data['email']
            request.session['order_email'] = email
            orders = Order.objects.filter(email=email).order_by('-created_at')
            total_spent = sum(o.total_price for o in orders)
    else:
        email_form = OrderEmailForm(initial={'email': email})

    context = {
        'orders': orders,
        'email_form': email_form,
        'email': email,
        'total_spent': total_spent,
    }
    return render(request, 'shop/orders_list.html', context)


@require_POST
@sensitive_post_parameters()
def order_cancel(request, order_id):
    """Отмена заказа — только если email совпадает с сессией"""
    order = get_object_or_404(Order, id=order_id)

    # IDOR protection: проверяем что email в сессии совпадает
    session_email = request.session.get('order_email', '')
    if session_email != order.email:
        messages.warning(
            request,
            'У вас нет доступа к этому заказу.'
        )
        return redirect('shop:orders_list')

    # Можно отменить только новые заказы
    if order.status not in ['new', 'processing']:
        messages.warning(request, 'Этот заказ уже не может быть отменён')
        return redirect('shop:orders_list')

    with transaction.atomic():
        # Возвращаем товары на склад
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()

        # Меняем статус на отменён
        old_status = order.status
        order.status = 'cancelled'
        order.save()

    logger.warning(
        f"Order #{order_id} cancelled by {order.email}. "
        f"Status: {old_status} -> cancelled"
    )

    messages.success(request, f'Заказ #{order.id} отменён. Товары возвращены на склад.')
    return redirect('shop:orders_list')
