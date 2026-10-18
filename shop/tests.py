from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from shop.models import Category, Product, Order, OrderItem


class CategoryModelTest(TestCase):
    """Тесты модели Category."""

    def setUp(self):
        self.category = Category.objects.create(
            name='Фрукты',
            slug='fruits',
            description='Свежие фрукты'
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Фрукты')

    def test_category_slug(self):
        self.assertEqual(self.category.slug, 'fruits')

    def test_category_default_order(self):
        Category.objects.create(name='Авокадо', slug='avocado')
        Category.objects.create(name='Бананы', slug='bananas')
        categories = list(Category.objects.all())
        self.assertEqual(categories[0].name, 'Авокадо')
        self.assertEqual(categories[1].name, 'Бананы')
        self.assertEqual(categories[2].name, 'Фрукты')


class ProductModelTest(TestCase):
    """Тесты модели Product."""

    def setUp(self):
        self.category = Category.objects.create(
            name='Молочные',
            slug='dairy'
        )
        self.product = Product.objects.create(
            name='Молоко',
            slug='milk',
            category=self.category,
            price=Decimal('89.90'),
            old_price=Decimal('120.00'),
            weight='1 л',
            stock=50,
            available=True,
            featured=True
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Молоко')

    def test_is_on_sale_true(self):
        self.assertTrue(self.product.is_on_sale)

    def test_discount_percentage(self):
        self.assertEqual(self.product.discount_percentage, 25)

    def test_is_in_stock_true(self):
        self.assertTrue(self.product.is_in_stock)

    def test_is_in_stock_no_stock(self):
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock)

    def test_is_in_stock_not_available(self):
        self.product.available = False
        self.product.save()
        self.assertFalse(self.product.is_in_stock)

    def test_product_absolute_url(self):
        url = self.product.get_absolute_url()
        self.assertEqual(url, '/catalog/milk/')

    def test_no_sale_when_no_old_price(self):
        self.product.old_price = None
        self.product.save()
        self.assertFalse(self.product.is_on_sale)


class CartModelTest(TestCase):
    """Тесты модели CartItem."""

    def setUp(self):
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            name='Тестовый товар',
            slug='test-product',
            category=self.category,
            price=Decimal('100.00'),
            stock=10
        )
        self.cart_item = self.product.cart_items.create(quantity=3)

    def test_cart_item_str(self):
        self.assertEqual(str(self.cart_item), 'Тестовый товар x 3')

    def test_cart_item_total_price(self):
        self.assertEqual(self.cart_item.total_price, Decimal('300.00'))


class OrderModelTest(TestCase):
    """Тесты модели Order."""

    def setUp(self):
        self.order = Order.objects.create(
            first_name='Иван',
            last_name='Иванов',
            email='ivan@test.com',
            phone='+79991234567',
            address='г. Москва, ул. Тестовая, 1',
            total_price=Decimal('500.00'),
            status='new'
        )

    def test_order_str(self):
        self.assertIn('Заказ #1', str(self.order))
        self.assertIn('Иван Иванов', str(self.order))

    def test_order_status_display(self):
        self.assertEqual(self.order.get_status_display(), 'Новый')

    def test_order_absolute_url(self):
        url = self.order.get_absolute_url()
        self.assertEqual(url, '/order/1/')


class OrderItemModelTest(TestCase):
    """Тесты модели OrderItem."""

    def setUp(self):
        self.order = Order.objects.create(
            first_name='Тест',
            last_name='Тест',
            email='test@test.com',
            phone='+79990000000',
            address='Тестовая ул, 1',
            total_price=Decimal('500.00')
        )
        self.category = Category.objects.create(name='Кат', slug='cat')
        self.product = Product.objects.create(
            name='Товар',
            slug='product',
            category=self.category,
            price=Decimal('250.00'),
            stock=10
        )
        self.item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name='Товар',
            quantity=2,
            price=Decimal('250.00')
        )

    def test_order_item_str(self):
        self.assertEqual(str(self.item), 'Товар x 2')

    def test_order_item_total_price(self):
        self.assertEqual(self.item.total_price, Decimal('500.00'))


class ViewTests(TestCase):
    """Тесты представлений."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Фрукты',
            slug='fruits',
            active=True
        )
        self.product = Product.objects.create(
            name='Яблоки',
            slug='apples',
            category=self.category,
            price=Decimal('150.00'),
            old_price=Decimal('200.00'),
            weight='1 кг',
            stock=100,
            available=True,
            featured=True
        )
        self.product2 = Product.objects.create(
            name='Бананы',
            slug='bananas',
            category=self.category,
            price=Decimal('100.00'),
            stock=50,
            available=True
        )

    # --- Главная страница ---
    def test_home_page_status_code(self):
        response = self.client.get(reverse('shop:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_context(self):
        response = self.client.get(reverse('shop:home'))
        self.assertContains(response, 'ФрешМаркет')
        self.assertIn('categories', response.context)
        self.assertIn('featured_products', response.context)
        self.assertIn('new_products', response.context)
        self.assertEqual(len(response.context['categories']), 1)
        self.assertEqual(len(response.context['featured_products']), 1)

    # --- Каталог ---
    def test_catalog_page_status_code(self):
        response = self.client.get(reverse('shop:catalog'))
        self.assertEqual(response.status_code, 200)

    def test_catalog_shows_products(self):
        response = self.client.get(reverse('shop:catalog'))
        self.assertContains(response, 'Яблоки')
        self.assertContains(response, 'Бананы')

    def test_category_detail_page(self):
        url = reverse('shop:category_detail', kwargs={'category_slug': 'fruits'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Яблоки')

    def test_catalog_search(self):
        response = self.client.get(
            reverse('shop:catalog'),
            {'q': 'Яблоки'}
        )
        self.assertContains(response, 'Яблоки')
        self.assertNotContains(response, 'Бананы')

    def test_catalog_sort_by_price_asc(self):
        response = self.client.get(
            reverse('shop:catalog'),
            {'sort': 'price_asc'}
        )
        products = list(response.context['products'])
        self.assertLessEqual(products[0].price, products[-1].price)

    def test_catalog_filter_by_price(self):
        response = self.client.get(
            reverse('shop:catalog'),
            {'min_price': '120', 'max_price': '200'}
        )
        products = list(response.context['products'])
        for p in products:
            self.assertGreaterEqual(p.price, Decimal('120'))
            self.assertLessEqual(p.price, Decimal('200'))

    def test_catalog_hidden_unavailable(self):
        self.product.available = False
        self.product.save()
        response = self.client.get(reverse('shop:catalog'))
        self.assertNotContains(response, 'Яблоки')

    # --- Страница товара ---
    def test_product_detail_status_code(self):
        response = self.client.get(
            reverse('shop:product_detail', kwargs={'product_slug': 'apples'})
        )
        self.assertEqual(response.status_code, 200)

    def test_product_detail_content(self):
        response = self.client.get(
            reverse('shop:product_detail', kwargs={'product_slug': 'apples'})
        )
        self.assertContains(response, 'Яблоки')
        self.assertContains(response, '150')
        self.assertContains(response, '1 кг')

    def test_unavailable_product_returns_404(self):
        self.product.available = False
        self.product.save()
        response = self.client.get(
            reverse('shop:product_detail', kwargs={'product_slug': 'apples'})
        )
        self.assertEqual(response.status_code, 404)

    # --- Корзина ---
    def test_cart_page_empty(self):
        response = self.client.get(reverse('shop:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'корзина пуста')

    def test_add_to_cart(self):
        session = self.client.session
        session['cart'] = {}
        session.save()

        response = self.client.post(
            reverse('shop:cart_add', kwargs={'product_slug': 'apples'}),
            {}
        )
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        cart = session.get('cart', {})
        self.assertIn(str(self.product.id), cart)
        self.assertEqual(cart[str(self.product.id)]['quantity'], 1)

    def test_add_to_cart_increments(self):
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 1, 'price': '150.00'}}
        session.save()

        self.client.post(
            reverse('shop:cart_add', kwargs={'product_slug': 'apples'}),
            {}
        )
        self.client.post(
            reverse('shop:cart_add', kwargs={'product_slug': 'apples'}),
            {}
        )
        session = self.client.session
        cart = session.get('cart', {})
        self.assertEqual(cart[str(self.product.id)]['quantity'], 3)

    def test_add_out_of_stock_fails(self):
        self.product.stock = 0
        self.product.save()
        session = self.client.session
        session['cart'] = {}
        session.save()

        response = self.client.post(
            reverse('shop:cart_add', kwargs={'product_slug': 'apples'}),
            {}
        )
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        cart = session.get('cart', {})
        self.assertNotIn(str(self.product.id), cart)

    def test_cart_page_with_items(self):
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {'quantity': 1, 'price': '150.00'}
        }
        session.save()

        response = self.client.get(reverse('shop:cart_detail'))
        self.assertContains(response, 'Яблоки')
        self.assertContains(response, '150')

    def test_remove_from_cart(self):
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 1, 'price': '150.00'}}
        session.save()

        response = self.client.post(
            reverse('shop:cart_remove', kwargs={'cart_item_id': self.product.id}),
            {}
        )
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        cart = session.get('cart', {})
        self.assertNotIn(str(self.product.id), cart)

    # --- Оформление заказа ---
    def test_checkout_empty_cart_redirect(self):
        response = self.client.get(reverse('shop:checkout'))
        self.assertEqual(response.status_code, 302)

    def test_checkout_with_cart(self):
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {'quantity': 1, 'price': '150.00'}
        }
        session.save()

        response = self.client.get(reverse('shop:checkout'))
        self.assertEqual(response.status_code, 200)

    def test_checkout_submit_valid(self):
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {'quantity': 1, 'price': '150.00'}
        }
        session.save()

        response = self.client.post(
            reverse('shop:checkout'),
            {
                'first_name': 'Иван',
                'last_name': 'Петров',
                'email': 'ivan@example.com',
                'phone': '+79991234567',
                'address': 'г. Москва, ул. Ленина, 1',
                'comment': 'Доставить утром',
            }
        )
        self.assertEqual(response.status_code, 302)
        # Проверяем, что заказ создан
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.first_name, 'Иван')
        self.assertEqual(order.total_price, Decimal('150.00'))
        # Проверяем, что корзина очищена
        session = self.client.session
        self.assertNotIn('cart', session)
        # Проверяем, что остаток уменьшился
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 99)

    def test_checkout_submit_invalid(self):
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {'quantity': 1, 'price': '150.00'}
        }
        session.save()

        response = self.client.post(
            reverse('shop:checkout'),
            {
                'first_name': '',
                'last_name': '',
                'email': '',
                'phone': '',
                'address': '',
                'comment': '',
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)

    # --- Страница заказа ---
    def test_order_detail_page(self):
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {'quantity': 1, 'price': '150.00'}
        }
        session.save()

        self.client.post(
            reverse('shop:checkout'),
            {
                'first_name': 'Иван',
                'last_name': 'Петров',
                'email': 'ivan@example.com',
                'phone': '+79991234567',
                'address': 'г. Москва, ул. Ленина, 1',
                'comment': '',
            }
        )
        response = self.client.get(reverse('shop:order_detail', kwargs={'order_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Заказ #1')
        self.assertContains(response, 'Иван')


class FormTests(TestCase):
    """Тесты форм."""

    def test_order_form_valid(self):
        from shop.forms import OrderCreateForm
        data = {
            'first_name': 'Иван',
            'last_name': 'Петров',
            'email': 'ivan@example.com',
            'phone': '+79991234567',
            'address': 'г. Москва, ул. Ленина, 1',
            'comment': 'Тест',
        }
        form = OrderCreateForm(data=data)
        self.assertTrue(form.is_valid())

    def test_order_form_invalid_empty(self):
        from shop.forms import OrderCreateForm
        form = OrderCreateForm(data={})
        self.assertFalse(form.is_valid())

    def test_product_search_form(self):
        from shop.forms import ProductSearchForm
        categories = Category.objects.all()
        form = ProductSearchForm(
            categories=categories,
            data={'query': 'молоко', 'category': '', 'min_price': '', 'max_price': ''}
        )
        self.assertTrue(form.is_valid())


class OrdersListTests(TestCase):
    """Тесты списка заказов."""

    def setUp(self):
        self.client = Client()
        self.user_email = 'testuser@example.com'
        # Создаём заказы
        self.order1 = Order.objects.create(
            first_name='Иван',
            last_name='Петров',
            email=self.user_email,
            phone='+79991111111',
            address='ул. Тестовая, 1',
            total_price=Decimal('500.00'),
            status='new'
        )
        self.order2 = Order.objects.create(
            first_name='Иван',
            last_name='Петров',
            email=self.user_email,
            phone='+79991111111',
            address='ул. Тестовая, 1',
            total_price=Decimal('1200.00'),
            status='delivered'
        )
        self.order3 = Order.objects.create(
            first_name='Другой',
            last_name='Пользователь',
            email='other@example.com',
            phone='+79992222222',
            address='ул. Другая, 2',
            total_price=Decimal('300.00'),
            status='processing'
        )

    def test_orders_list_empty(self):
        """Пустая страница заказов без email."""
        response = self.client.get(reverse('shop:orders_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Введите email')

    def test_orders_list_with_email(self):
        """Показ заказов по email."""
        response = self.client.post(
            reverse('shop:orders_list'),
            {'email': self.user_email}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Заказ #1')
        self.assertContains(response, 'Заказ #2')
        self.assertNotContains(response, 'Заказ #3')

    def test_orders_list_different_email(self):
        """Заказы другого email не показываются."""
        response = self.client.post(
            reverse('shop:orders_list'),
            {'email': 'other@example.com'}
        )
        self.assertContains(response, 'Заказ #3')
        self.assertNotContains(response, 'Заказ #1')

    def test_orders_list_order_email_in_session(self):
        """Email сохраняется в сессии."""
        self.client.post(
            reverse('shop:orders_list'),
            {'email': self.user_email}
        )
        session = self.client.session
        self.assertEqual(session.get('order_email'), self.user_email)


class OrderCancelTests(TestCase):
    """Тесты отмены заказа."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            name='Товар',
            slug='test-product',
            category=self.category,
            price=Decimal('100.00'),
            stock=50
        )
        self.order_new = Order.objects.create(
            first_name='Иван',
            last_name='Петров',
            email='test@test.com',
            phone='+79990000000',
            address='Тестовая ул, 1',
            total_price=Decimal('100.00'),
            status='new'
        )
        self.order_processing = Order.objects.create(
            first_name='Иван',
            last_name='Петров',
            email='test@test.com',
            phone='+79990000000',
            address='Тестовая ул, 1',
            total_price=Decimal('200.00'),
            status='processing'
        )
        self.order_delivered = Order.objects.create(
            first_name='Иван',
            last_name='Петров',
            email='test@test.com',
            phone='+79990000000',
            address='Тестовая ул, 1',
            total_price=Decimal('300.00'),
            status='delivered'
        )
        self.order_cancelled = Order.objects.create(
            first_name='Иван',
            last_name='Петров',
            email='test@test.com',
            phone='+79990000000',
            address='Тестовая ул, 1',
            total_price=Decimal('400.00'),
            status='cancelled'
        )
        # Добавляем позицию в заказ
        OrderItem.objects.create(
            order=self.order_new,
            product=self.product,
            product_name='Товар',
            quantity=1,
            price=Decimal('100.00')
        )

    def test_cancel_new_order(self):
        """Отмена заказа со статусом 'new'."""
        session = self.client.session
        session['order_email'] = 'test@test.com'
        session.save()
        response = self.client.post(
            reverse('shop:order_cancel', kwargs={'order_id': self.order_new.id})
        )
        self.assertEqual(response.status_code, 302)  # redirect
        self.order_new.refresh_from_db()
        self.assertEqual(self.order_new.status, 'cancelled')
        # Товар должен вернуться на склад
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 51)

    def test_cancel_processing_order(self):
        """Отмена заказа со статусом 'processing'."""
        session = self.client.session
        session['order_email'] = 'test@test.com'
        session.save()
        response = self.client.post(
            reverse('shop:order_cancel', kwargs={'order_id': self.order_processing.id})
        )
        self.assertEqual(response.status_code, 302)
        self.order_processing.refresh_from_db()
        self.assertEqual(self.order_processing.status, 'cancelled')

    def test_cannot_cancel_delivered_order(self):
        """Нельзя отменить доставленный заказ."""
        session = self.client.session
        session['order_email'] = 'test@test.com'
        session.save()
        response = self.client.post(
            reverse('shop:order_cancel', kwargs={'order_id': self.order_delivered.id})
        )
        self.assertEqual(response.status_code, 302)
        self.order_delivered.refresh_from_db()
        self.assertEqual(self.order_delivered.status, 'delivered')  # без изменений

    def test_cannot_cancel_already_cancelled(self):
        """Нельзя отменить уже отменённый заказ."""
        session = self.client.session
        session['order_email'] = 'test@test.com'
        session.save()
        response = self.client.post(
            reverse('shop:order_cancel', kwargs={'order_id': self.order_cancelled.id})
        )
        self.assertEqual(response.status_code, 302)
        self.order_cancelled.refresh_from_db()
        self.assertEqual(self.order_cancelled.status, 'cancelled')

    def test_cannot_cancel_wrong_email(self):
        """Нельзя отменить чужой заказ (IDOR protection)."""
        # Email в сессии не совпадает с email заказа
        session = self.client.session
        session['order_email'] = 'wrong@email.com'
        session.save()
        response = self.client.post(
            reverse('shop:order_cancel', kwargs={'order_id': self.order_new.id})
        )
        self.assertEqual(response.status_code, 302)  # redirect
        self.order_new.refresh_from_db()
        self.assertEqual(self.order_new.status, 'new')  # без изменений


class CheckoutSessionEmailTests(TestCase):
    """Тесты сохранения email в сессии при оформлении заказа."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            name='Товар',
            slug='test-product',
            category=self.category,
            price=Decimal('150.00'),
            stock=100
        )

    def test_email_saved_in_session_after_checkout(self):
        """Email сохраняется в сессии после оформления заказа."""
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 1, 'price': '150.00'}}
        session.save()

        self.client.post(
            reverse('shop:checkout'),
            {
                'first_name': 'Иван',
                'last_name': 'Петров',
                'email': 'ivan@example.com',
                'phone': '+79991234567',
                'address': 'г. Москва, ул. Ленина, 1',
                'comment': '',
            }
        )
        session = self.client.session
        self.assertEqual(session.get('order_email'), 'ivan@example.com')

    def test_email_saved_on_order_detail_view(self):
        """Email сохраняется при просмотре заказа."""
        session = self.client.session
        session['cart'] = {str(self.product.id): {'quantity': 1, 'price': '150.00'}}
        session.save()

        self.client.post(
            reverse('shop:checkout'),
            {
                'first_name': 'Иван',
                'last_name': 'Петров',
                'email': 'test2@example.com',
                'phone': '+79991234567',
                'address': 'г. Москва, ул. Ленина, 1',
                'comment': '',
            }
        )
        # При просмотре заказа email тоже сохраняется
        self.client.get(reverse('shop:order_detail', kwargs={'order_id': 1}))
        session = self.client.session
        self.assertEqual(session.get('order_email'), 'test2@example.com')
