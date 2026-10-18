from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'comment']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иван',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ivan@example.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'г. Москва, ул. Примерная, д. 1, кв. 1',
                'rows': 3,
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Комментарий к заказу (необязательно)',
                'rows': 3,
            }),
        }


class OrderEmailForm(forms.Form):
    email = forms.EmailField(
        label='Ваш email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ivan@example.com',
        })
    )


class ProductSearchForm(forms.Form):
    query = forms.CharField(
        label='Поиск',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск продуктов...',
        })
    )
    category = forms.ChoiceField(
        label='Категория',
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    min_price = forms.DecimalField(
        label='Мин. цена',
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
        })
    )
    max_price = forms.DecimalField(
        label='Макс. цена',
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '99999',
        })
    )

    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        if categories is not None:
            self.fields['category'].choices = [('', 'Все категории')] + [
                (cat.slug, cat.name) for cat in categories
            ]
