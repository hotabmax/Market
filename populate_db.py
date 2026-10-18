#!/usr/bin/env python
"""Скрипт для заполнения базы данных тестовыми продуктами."""
import os
import sys
import django

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')
django.setup()

from shop.models import Category, Product


def create_categories():
    """Создаёт категории продуктов."""
    categories_data = [
        {
            'name': 'Фрукты и овощи',
            'slug': 'fruits-vegetables',
            'description': 'Свежие фрукты и овощи каждый день',
        },
        {
            'name': 'Молочные продукты',
            'slug': 'dairy',
            'description': 'Молоко, сыр, йогурты и другие молочные продукты',
        },
        {
            'name': 'Хлеб и выпечка',
            'slug': 'bread',
            'description': 'Свежий хлеб и кондитерские изделия',
        },
        {
            'name': 'Мясо и птица',
            'slug': 'meat',
            'description': 'Свежее мясо и птица от проверенных поставщиков',
        },
        {
            'name': 'Рыба и морепродукты',
            'slug': 'fish',
            'description': 'Свежая рыба и морепродукты',
        },
        {
            'name': 'Напитки',
            'slug': 'drinks',
            'description': 'Соки, вода, чай и кофе',
        },
    ]

    categories = {}
    for data in categories_data:
        cat, created = Category.objects.get_or_create(
            slug=data['slug'],
            defaults=data
        )
        categories[data['slug']] = cat
        if created:
            print(f'  + Создана категория: {cat.name}')
        else:
            print(f'  ~ Категория уже существует: {cat.name}')

    return categories


def create_products(categories):
    """Создаёт продукты питания."""
    products_data = [
        # Фрукты и овощи
        {'name': 'Яблоки Гала', 'category': 'fruits-vegetables', 'price': '189.90', 'old_price': '249.90',
         'weight': '1 кг', 'stock': 150, 'featured': True,
         'short_description': 'Сладкие красные яблоки',
         'description': 'Свежие яблоки сорта Гала. Сладкие, сочные, идеальны для употребления в свежем виде, выпечки и салатов. Выращены в экологически чистых садах.'},
        {'name': 'Бананы', 'category': 'fruits-vegetables', 'price': '119.90',
         'weight': '1 кг', 'stock': 200, 'featured': True,
         'short_description': 'Спелые эквадорские бананы',
         'description': 'Спелые бананы высшего сорта. Отличный источник калия и энергии. Идеальны для завтрака и перекуса.'},
        {'name': 'Помидоры черри', 'category': 'fruits-vegetables', 'price': '349.90', 'old_price': '429.90',
         'weight': '500 г', 'stock': 80, 'featured': True,
         'short_description': 'Сладкие мини-помидоры',
         'description': 'Сладкие помидоры черри на ветке. Идеальны для салатов и закусок. Выращены в теплицах без пестицидов.'},
        {'name': 'Огурцы свежие', 'category': 'fruits-vegetables', 'price': '159.90',
         'weight': '1 кг', 'stock': 120,
         'short_description': 'Свежие хрустящие огурцы',
         'description': 'Свежие огурцы грунтовые. Хрустящие и ароматные, отлично подходят для салатов и консервации.'},
        {'name': 'Авокадо Хасс', 'category': 'fruits-vegetables', 'price': '299.90',
         'weight': '1 шт (~200 г)', 'stock': 60, 'featured': True,
         'short_description': 'Спелый авокадо для тостов и салатов',
         'description': 'Спелый авокадо сорта Хасс. Кремовая текстура, ореховый вкус. Идеален для тостов, салатов и гуакамоле.'},
        {'name': 'Брокколи', 'category': 'fruits-vegetables', 'price': '219.90',
         'weight': '400 г', 'stock': 70,
         'short_description': 'Свежий полезный овощ',
         'description': 'Свежая брокколи. Богата витаминами C и K, клетчаткой и антиоксидантами. Отлично подходит для приготовления на пару.'},

        # Молочные продукты
        {'name': 'Молоко 3.2%', 'category': 'dairy', 'price': '89.90',
         'weight': '1 л', 'stock': 300, 'featured': True,
         'short_description': 'Фермерское молоко',
         'description': 'Пастеризованное молоко фермерского производства. Жирность 3.2%. Отличный вкус и качество.'},
        {'name': 'Сыр Российский', 'category': 'dairy', 'price': '749.90', 'old_price': '899.90',
         'weight': '1 кг', 'stock': 40, 'featured': True,
         'short_description': 'Классический полутвёрдый сыр',
         'description': 'Российский сыр полутвёрдый. Нежный сливочный вкус, отлично подходит для бутербродов и горячих блюд.'},
        {'name': 'Йогурт греческий', 'category': 'dairy', 'price': '129.90',
         'weight': '200 г', 'stock': 200,
         'short_description': 'Натуральный греческий йогурт',
         'description': 'Натуральный греческий йогурт без добавок. Высокое содержание белка, густая кремовая текстура.'},
        {'name': 'Масло сливочное 82.5%', 'category': 'dairy', 'price': '189.90',
         'weight': '200 г', 'stock': 150, 'featured': True,
         'short_description': 'Натуральное сливочное масло',
         'description': 'Натуральное сливочное масло жирностью 82.5%. Изготовлено из фермерских сливок. Идеально для завтраков.'},
        {'name': 'Творог 5%', 'category': 'dairy', 'price': '109.90',
         'weight': '200 г', 'stock': 180,
         'short_description': 'Мягкий зернёный творог',
         'description': 'Зернёный творог жирностью 5%. Нежная текстура, мягкий вкус. Богат кальцием и белком.'},

        # Хлеб и выпечка
        {'name': 'Хлеб белый', 'category': 'bread', 'price': '59.90',
         'weight': '400 г', 'stock': 100,
         'short_description': 'Свежий пшеничный хлеб',
         'description': 'Свежий пшеничный хлеб из муки высшего сорта. Мягкий, ароматный, с хрустящей корочкой.'},
        {'name': 'Круассан с маслом', 'category': 'bread', 'price': '89.90',
         'weight': '80 г', 'stock': 50, 'featured': True,
         'short_description': 'Хрустящий французский круассан',
         'description': 'Нежный французский круассан с настоящим сливочным маслом. Выпекается каждое утро. Идеален к кофе.'},
        {'name': 'Багет французский', 'category': 'bread', 'price': '79.90',
         'weight': '250 г', 'stock': 40,
         'short_description': 'Классический французский багет',
         'description': 'Хрустящий французский багет с нежным мякишем. Идеален для бутербродов и брускетт.'},
        {'name': 'Булочка с корицей', 'category': 'bread', 'price': '69.90',
         'weight': '100 г', 'stock': 60, 'featured': True,
         'short_description': 'Ароматная сладкая булочка',
         'description': 'Пышная булочка с ароматной корицей и сахарной пудрой. Отличный выбор к чаю или кофе.'},

        # Мясо и птица
        {'name': 'Куриная грудка', 'category': 'meat', 'price': '389.90',
         'weight': '1 кг', 'stock': 100, 'featured': True,
         'short_description': 'Свежая куриная грудка',
         'description': 'Свежая куриная грудка на кости. Диетическое мясо с высоким содержанием белка. Выращена без антибиотиков.'},
        {'name': 'Стейк говяжий', 'category': 'meat', 'price': '1299.90', 'old_price': '1599.90',
         'weight': '300 г', 'stock': 30, 'featured': True,
         'short_description': 'Мраморная говядина для стейка',
         'description': 'Стейк из мраморной говядины. Идеально подходит для приготовления на гриле или сковороде. Средняя прожарка — medium rare.'},
        {'name': 'Фарш домашний', 'category': 'meat', 'price': '499.90',
         'weight': '500 г', 'stock': 80,
         'short_description': 'Фарш из свинины и говядины',
         'description': 'Домашний фарш из свинины и говядины в пропорции 50/50. Свежий, без добавок. Для котлет и тефтелей.'},
        {'name': 'Куриные бёдрышки', 'category': 'meat', 'price': '289.90',
         'weight': '1 кг', 'stock': 90,
         'short_description': 'Сочные куриные бёдрышки',
         'description': 'Куриные бёдрышки свежие. Нежное мясо на кости. Отлично подходят для запекания и жарки.'},

        # Рыба и морепродукты
        {'name': 'Лосось филе', 'category': 'fish', 'price': '1499.90', 'old_price': '1799.90',
         'weight': '500 г', 'stock': 25, 'featured': True,
         'short_description': 'Свежее филе лосося',
         'description': 'Свежее филе лосося атлантического. Нежное, розовое мясо. Идеально для запекания, суши и стейков.'},
        {'name': 'Тунец филе', 'category': 'fish', 'price': '1199.90',
         'weight': '300 г', 'stock': 20,
         'short_description': 'Филе тунца для стейков',
         'description': 'Филе тунца высшего сорта. Плотная текстура, насыщенный вкус. Отлично подходит для стейков и суши.'},
        {'name': 'Креветки тигровые', 'category': 'fish', 'price': '899.90',
         'weight': '500 г', 'stock': 35, 'featured': True,
         'short_description': 'Крупные замороженные креветки',
         'description': 'Крупные тигровые креветки. Размер L-XL. Заморожены сразу после вылова для сохранения свежести.'},
        {'name': 'Минтай филе', 'category': 'fish', 'price': '449.90',
         'weight': '500 г', 'stock': 60,
         'short_description': 'Диетическое белое филе',
         'description': 'Филе минтая без кожи и костей. Диетический продукт с нежным вкусом. Низкое содержание калорий.'},

        # Напитки
        {'name': 'Сок апельсиновый', 'category': 'drinks', 'price': '149.90',
         'weight': '1 л', 'stock': 150, 'featured': True,
         'short_description': '100% натуральный сок',
         'description': 'Апельсиновый сок прямого отжима. Без сахара и консервантов. Богат витамином C.'},
        {'name': 'Вода минеральная', 'category': 'drinks', 'price': '59.90',
         'weight': '1.5 л', 'stock': 500,
         'short_description': 'Природная минеральная вода',
         'description': 'Природная негазированная минеральная вода из артезианского источника. Содержит полезные минералы.'},
        {'name': 'Кофе зерновой', 'category': 'drinks', 'price': '899.90', 'old_price': '1099.90',
         'weight': '1 кг', 'stock': 70, 'featured': True,
         'short_description': 'Арабика 100%',
         'description': '100% арабика средней обжарки. Ноты шоколада и орехов. Зерно обжарено недавно, свежесть гарантирована.'},
        {'name': 'Чай зелёный', 'category': 'drinks', 'price': '349.90',
         'weight': '100 г', 'stock': 120,
         'short_description': 'Японский зелёный чай сенча',
         'description': 'Высококачественный японский зелёный чай сенча. Нежный травянистый вкус, богат антиоксидантами.'},
        {'name': 'Лимонад домашний', 'category': 'drinks', 'price': '129.90',
         'weight': '0.5 л', 'stock': 80,
         'short_description': 'Освежающий лимонад с мятой',
         'description': 'Домашний лимонад с натуральным лимоном и свежей мятой. Без искусственных красителей и ароматизаторов.'},
    ]

    count = 0
    for data in products_data:
        category = categories[data.pop('category')]
        slug = data['name'].lower().replace(' ', '-')

        product, created = Product.objects.get_or_create(
            slug=slug,
            defaults={**data, 'category': category}
        )

        if created:
            print(f'  + Создан товар: {product.name} — {product.price}')
        else:
            print(f'  ~ Товар уже существует: {product.name}')
        count += 1

    return count


def main():
    print('Creating categories...')
    categories = create_categories()

    print('\nCreating products...')
    count = create_products(categories)

    print(f'\nDone! Created {count} products in {len(categories)} categories.')
    print('\nTo upload images, open admin panel:')
    print('  http://127.0.0.1:8000/admin/')
    print('  Login: admin / Password: admin123')


if __name__ == '__main__':
    main()
