from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('user', 'name')
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Net Banking', 'Net Banking'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Cash')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def clean(self):
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({'amount': 'Amount must be greater than zero.'})
        if self.date and self.date > timezone.now().date():
            raise ValidationError({'date': 'Date cannot be in the future.'})
        if self.category_id and self.user_id and self.category.user_id != self.user_id:
            raise ValidationError({'category': 'Choose one of your own categories.'})

    def __str__(self):
        return f'{self.title} - {self.amount}'


class Budget(models.Model):
    """Optional extra: monthly spending limit per category."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'category')

    def clean(self):
        if self.monthly_limit is not None and self.monthly_limit <= 0:
            raise ValidationError({'monthly_limit': 'The monthly limit must be greater than zero.'})
        if self.category_id and self.user_id and self.category.user_id != self.user_id:
            raise ValidationError({'category': 'Choose one of your own categories.'})

    def __str__(self):
        return f'{self.category} - {self.monthly_limit}'