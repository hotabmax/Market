from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Каталог
    path('catalog/', views.catalog, name='catalog'),
    
    # Товар (должен быть ДО категории!)
    path('catalog/<slug:product_slug>/', views.product_detail, name='product_detail'),
    
    # Категория
    path('catalog/category/<slug:category_slug>/', views.catalog, name='category_detail'),
    
    # Товар
    path('catalog/<slug:product_slug>/', views.product_detail, name='product_detail'),
    
    # Корзина
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<slug:product_slug>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:cart_item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/', views.cart_update, name='cart_update'),
    
    # Оформление заказа
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders_list, name='orders_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),
]
