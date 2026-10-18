from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['active', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'stock', 'stock_status',
        'available', 'featured', 'is_on_sale_badge', 'created_at'
    ]
    list_filter = ['category', 'available', 'stock_status', 'featured', 'created_at']
    list_editable = ['price', 'stock', 'available', 'featured']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    raw_id_fields = ['category']

    def is_on_sale_badge(self, obj):
        if obj.is_on_sale:
            return format_html(
                '<span style="color: green; font-weight: bold;">Скидка {}%</span>',
                obj.discount_percentage
            )
        return '—'
    is_on_sale_badge.short_description = 'Скидка'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'quantity', 'price', 'total_price']

    @admin.display(description='Сумма')
    def total_price(self, obj):
        return f"{obj.total_price:.2f} ₽"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'first_name', 'last_name', 'email', 'phone',
        'total_price', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    inlines = [OrderItemInline]
    readonly_fields = ['total_price', 'created_at', 'updated_at']
