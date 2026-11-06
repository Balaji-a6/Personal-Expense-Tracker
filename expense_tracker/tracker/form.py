from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Budget, Expense, Category


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email address already exists.')
        return email


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'required': True})

    class Meta:
        model = Category
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if self.user and Category.objects.filter(user=self.user, name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError('You already have a category with this name.')
        return name


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date', 'payment_method', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 100, 'required': True}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'required': True}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'payment_method': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['category'].required = False
        self.fields['date'].widget.attrs['max'] = timezone.localdate().isoformat()


class ExpenseFilterForm(forms.Form):
    q = forms.CharField(required=False, label='Search', widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Search title or notes',
    }))
    category = forms.ChoiceField(required=False, label='Category', choices=(), widget=forms.Select(attrs={'class': 'form-select'}))
    start = forms.DateField(required=False, label='From', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    end = forms.DateField(required=False, label='To', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    min = forms.DecimalField(required=False, min_value=0, label='Min amount', widget=forms.NumberInput(attrs={
        'class': 'form-control', 'step': '0.01', 'min': '0',
    }))
    max = forms.DecimalField(required=False, min_value=0, label='Max amount', widget=forms.NumberInput(attrs={
        'class': 'form-control', 'step': '0.01', 'min': '0',
    }))

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = [('', 'All categories')] + [
            (str(category.pk), category.name)
            for category in Category.objects.filter(user=user)
        ]

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        minimum = cleaned_data.get('min')
        maximum = cleaned_data.get('max')
        if start and end and start > end:
            self.add_error('end', 'The end date must be on or after the start date.')
        if minimum is not None and maximum is not None and minimum > maximum:
            self.add_error('max', 'The maximum amount must be at least the minimum amount.')
        return cleaned_data


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'monthly_limit']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'monthly_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'required': True}),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)

    def clean_monthly_limit(self):
        limit = self.cleaned_data['monthly_limit']
        if limit <= 0:
            raise ValidationError('The monthly limit must be greater than zero.')
        return limit