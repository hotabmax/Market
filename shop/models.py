from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Категории продуктов"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', max_length=100, unique=True)
    image = models.ImageField('Изображение', upload_to='categories/', blank=True, null=True)
    description = models.TextField('Описание', blank=True)
    active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:category_detail', kwargs={'category_slug': self.slug})


class Product(models.Model):
    """Товары (продукты питания)"""
    AVAILABLE = 'available'
    OUT_OF_STOCK = 'out_of_stock'

    STOCK_CHOICES = [
        (AVAILABLE, 'В наличии'),
        (OUT_OF_STOCK, 'Нет в наличии'),
    ]

    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    description = models.TextField('Описание', blank=True)
    short_description = models.CharField('Краткое описание', max_length=300, blank=True)
    image = models.ImageField('Изображение', upload_to='products/', blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    old_price = models.DecimalField('Старая цена', max_digits=10, decimal_places=2, blank=True, null=True)
    weight = models.CharField('Вес/Объём', max_length=50, blank=True)
    stock = models.PositiveIntegerField('Остаток', default=0)
    available = models.BooleanField('Доступен', default=True)
    stock_status = models.CharField('Статус', max_length=20, choices=STOCK_CHOICES, default=AVAILABLE)
    featured = models.BooleanField('Рекомендуемый', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-featured', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'available']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'product_slug': self.slug})

    @property
    def is_on_sale(self):
        return bool(self.old_price and self.old_price > self.price)

    @property
    def discount_percentage(self):
        if self.is_on_sale and self.old_price:
            return round((self.old_price - self.price) / self.old_price * 100)
        return 0

    @property
    def is_in_stock(self):
        return self.stock > 0 and self.available


class CartItem(models.Model):
    """Позиции корзины"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField('Количество', default=1)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """Заказы"""
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    EMAIL = 'email'
    PHONE = 'phone'
    ADDRESS = 'address'

    CONTACT_CHOICES = [
        (FIRST_NAME, 'Имя'),
        (LAST_NAME, 'Фамилия'),
        (EMAIL, 'Email'),
        (PHONE, 'Телефон'),
        (ADDRESS, 'Адрес доставки'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20)
    address = models.TextField('Адрес доставки')
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    total_price = models.DecimalField('Итого', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} - {self.first_name} {self.last_name}'

    def get_absolute_url(self):
        return reverse('shop:order_detail', kwargs={'order_id': self.id})


class OrderItem(models.Model):
    """Позиции заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    product_name = models.CharField('Название товара', max_length=200)
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    @property
    def total_price(self):
        return self.price * self.quantity
