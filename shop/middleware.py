"""
Middleware для rate limiting и защиты от манипуляций.
"""
import time
import logging
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger('security')


class RateLimitMiddleware:
    """
    Простой rate limiter на основе IP и session.
    Использует cache для хранения счётчиков.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Rate limiting для cart_add
        if view_func.__name__ == 'cart_add' and request.method == 'POST':
            if not self._check_rate_limit(request, 'cart_add'):
                return JsonResponse(
                    {'error': 'Слишком много запросов. Попробуйте позже.'},
                    status=429
                )

        # Rate limiting для order_cancel
        if view_func.__name__ == 'order_cancel' and request.method == 'POST':
            if not self._check_rate_limit(request, 'order_cancel'):
                return JsonResponse(
                    {'error': 'Слишком много запросов. Попробуйте позже.'},
                    status=429
                )

        return None

    def _check_rate_limit(self, request, endpoint):
        """Проверяет лимит запросов."""
        rate_config = getattr(settings, 'RATE_LIMIT', {})
        config = rate_config.get(endpoint, {})

        if not config:
            return True

        max_requests = config.get('max_requests', 10)
        window = config.get('window', 60)

        # Используем session key как идентификатор
        identifier = request.session.session_key or request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f"ratelimit:{endpoint}:{identifier}"

        current = cache.get(cache_key, 0)

        if current >= max_requests:
            logger.warning(
                f"Rate limit exceeded for {endpoint} from {identifier}"
            )
            return False

        cache.set(cache_key, current + 1, window)
        return True


class SecureCartMiddleware:
    """
    Защищает корзину от манипуляций:
    - Проверяет что цена в сессии совпадает с ценой в БД
    - Очищает невалидные данные
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.__name__ in ('cart_add', 'cart_update', 'cart_detail', 'checkout'):
            self._sanitize_cart(request)
        return None

    def _sanitize_cart(self, request):
        """Проверяет и очищает корзину от невалидных данных."""
        from shop.models import Product

        cart = request.session.get('cart', {})

        if not cart:
            return

        sanitized_cart = {}

        for product_id_str, data in list(cart.items()):
            try:
                product_id = int(product_id_str)
            except (ValueError, TypeError):
                continue

            try:
                product = Product.objects.get(id=product_id, available=True)
            except Product.DoesNotExist:
                continue

            # Проверяем количество
            quantity = data.get('quantity', 1)
            try:
                quantity = int(quantity)
            except (ValueError, TypeError):
                quantity = 1

            if quantity <= 0:
                continue

            # Ограничиваем максимальным остатком
            quantity = min(quantity, product.stock)

            # ВАЖНО: цену берём ТОЛЬКО из БД, игнорируем сессию
            sanitized_cart[str(product_id)] = {
                'quantity': quantity,
                'price': str(product.price),  # Для отображения, но не для расчётов
            }

        # Если корзина изменилась, сохраняем
        if sanitized_cart != cart:
            request.session['cart'] = sanitized_cart
