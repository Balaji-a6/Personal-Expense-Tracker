from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .form import ExpenseForm
from .models import Budget, Category, Expense


class ExpenseTrackerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='balaji',
            email='balaji@example.com',
            password='A-strong-password-96',
        )
        self.category = Category.objects.create(user=self.user, name='Food')
        self.client.force_login(self.user)

    def expense_data(self, **overrides):
        data = {
            'title': 'Lunch',
            'amount': '250.50',
            'date': timezone.localdate().isoformat(),
            'category': str(self.category.pk),
            'payment_method': 'UPI',
            'notes': 'Lunch near college',
        }
        data.update(overrides)
        return data

    def test_registration_password_hash_and_duplicate_email(self):
        self.client.logout()
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'A-strong-password-97',
            'password2': 'A-strong-password-97',
        })
        self.assertRedirects(response, reverse('dashboard'))
        new_user = User.objects.get(username='newuser')
        self.assertTrue(new_user.check_password('A-strong-password-97'))
        self.assertNotEqual(new_user.password, 'A-strong-password-97')

        self.client.logout()
        response = self.client.post(reverse('register'), {
            'username': 'anotheruser',
            'email': 'NEW@example.com',
            'password1': 'A-strong-password-98',
            'password2': 'A-strong-password-98',
        })
        self.assertContains(response, 'account with this email', status_code=200)
        self.assertFalse(User.objects.filter(username='anotheruser').exists())

        response = self.client.post(reverse('register'), {
            'username': 'balaji',
            'email': 'new-address@example.com',
            'password1': 'A-strong-password-98',
            'password2': 'A-strong-password-98',
        })
        self.assertIn('username', response.context['form'].errors)
        self.assertFalse(User.objects.filter(email='new-address@example.com').exists())

    def test_login_and_logout(self):
        self.client.logout()
        response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': 'A-strong-password-96',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_private_pages_require_authentication(self):
        self.client.logout()
        for name in ('dashboard', 'expense_list', 'expense_add', 'category_list', 'budget_list'):
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)

    def test_expense_create_edit_and_delete(self):
        response = self.client.post(reverse('expense_add'), self.expense_data())
        self.assertRedirects(response, reverse('expense_list'))
        expense = Expense.objects.get(user=self.user)
        self.assertEqual(expense.amount, Decimal('250.50'))

        response = self.client.post(
            reverse('expense_edit', args=[expense.pk]),
            self.expense_data(title='Updated lunch', amount='300.00'),
        )
        self.assertRedirects(response, reverse('expense_list'))
        expense.refresh_from_db()
        self.assertEqual(expense.title, 'Updated lunch')

        response = self.client.get(reverse('expense_delete', args=[expense.pk]))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('expense_delete', args=[expense.pk]))
        self.assertRedirects(response, reverse('expense_list'))
        self.assertFalse(Expense.objects.filter(pk=expense.pk).exists())

    def test_server_side_expense_validation(self):
        invalid_amount = ExpenseForm(self.expense_data(amount='0'), user=self.user)
        self.assertFalse(invalid_amount.is_valid())
        self.assertIn('amount', invalid_amount.errors)

        future_date = (timezone.localdate() + timedelta(days=1)).isoformat()
        future_expense = ExpenseForm(self.expense_data(date=future_date), user=self.user)
        self.assertFalse(future_expense.is_valid())
        self.assertIn('date', future_expense.errors)

        missing_title = ExpenseForm(self.expense_data(title='  '), user=self.user)
        self.assertFalse(missing_title.is_valid())
        self.assertIn('title', missing_title.errors)

    def test_user_cannot_view_or_assign_another_users_expenses_or_categories(self):
        other_user = User.objects.create_user(username='other', password='A-strong-password-99')
        other_category = Category.objects.create(user=other_user, name='Private')
        other_expense = Expense.objects.create(
            user=other_user,
            category=other_category,
            title='Private expense',
            amount=Decimal('99.00'),
            date=timezone.localdate(),
        )

        self.assertEqual(
            self.client.get(reverse('expense_edit', args=[other_expense.pk])).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse('expense_delete', args=[other_expense.pk])).status_code,
            404,
        )
        self.assertNotContains(self.client.get(reverse('expense_list')), 'Private expense')

        response = self.client.post(
            reverse('expense_add'),
            self.expense_data(category=str(other_category.pk)),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Expense.objects.filter(user=self.user).exists())

    def test_search_filters_and_pagination(self):
        for index in range(12):
            Expense.objects.create(
                user=self.user,
                category=self.category,
                title=f'Coffee {index}',
                amount=Decimal('10.00') + index,
                date=timezone.localdate(),
                notes='campus cafe',
            )
        response = self.client.get(reverse('expense_list'), {
            'q': 'campus',
            'category': str(self.category.pk),
            'start': timezone.localdate().isoformat(),
            'end': timezone.localdate().isoformat(),
            'min': '10',
            'max': '21',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'].paginator.count, 12)
        self.assertEqual(len(response.context['page'].object_list), 10)
        self.assertContains(response, f'category={self.category.pk}')

        response = self.client.get(reverse('expense_list'), {'q': 'campus', 'page': '2'})
        self.assertEqual(response.context['page'].number, 2)
        self.assertEqual(len(response.context['page'].object_list), 2)
        self.assertContains(response, 'q=campus&amp;page=1')

    def test_invalid_filters_are_reported_and_do_not_raise(self):
        response = self.client.get(reverse('expense_list'), {
            'start': '2026-10-10',
            'end': '2026-10-01',
            'min': '50',
            'max': '10',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('end', response.context['filter_form'].errors)
        self.assertIn('max', response.context['filter_form'].errors)

    def test_category_duplicates_are_rejected_case_insensitively(self):
        response = self.client.post(reverse('category_add'), {'name': ' food '})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Category.objects.filter(user=self.user).count(), 1)
        self.assertIn('name', response.context['form'].errors)
        self.assertContains(self.client.get(reverse('category_list')), 'Food')

    def test_category_and_budget_creation_and_budget_update(self):
        response = self.client.post(reverse('category_add'), {'name': 'Travel'})
        self.assertRedirects(response, reverse('category_list'))
        category = Category.objects.get(user=self.user, name='Travel')

        response = self.client.post(reverse('budget_add'), {
            'category': str(category.pk),
            'monthly_limit': '1000.00',
        })
        self.assertRedirects(response, reverse('budget_list'))
        self.assertEqual(Budget.objects.filter(user=self.user).count(), 1)

        response = self.client.post(reverse('budget_add'), {
            'category': str(category.pk),
            'monthly_limit': '1500.00',
        })
        self.assertRedirects(response, reverse('budget_list'))
        budget = Budget.objects.get(user=self.user, category=category)
        self.assertEqual(Budget.objects.filter(user=self.user).count(), 1)
        self.assertEqual(budget.monthly_limit, Decimal('1500.00'))

    def test_expense_search_matches_titles(self):
        Expense.objects.create(
            user=self.user,
            category=self.category,
            title='Coffee at campus',
            amount=Decimal('12.00'),
            date=timezone.localdate(),
        )
        response = self.client.get(reverse('expense_list'), {'q': 'coffee'})
        self.assertEqual(response.context['page'].paginator.count, 1)
        self.assertContains(response, 'Coffee at campus')

    def test_budget_progress_is_per_user_and_current_month(self):
        Budget.objects.create(user=self.user, category=self.category, monthly_limit=Decimal('500.00'))
        Expense.objects.create(
            user=self.user,
            category=self.category,
            title='Groceries',
            amount=Decimal('600.00'),
            date=timezone.localdate(),
        )
        response = self.client.get(reverse('dashboard'))
        budget = response.context['budgets'][0]
        self.assertEqual(budget['spent'], Decimal('600.00'))
        self.assertTrue(budget['exceeded'])
        self.assertEqual(budget['overage'], Decimal('100.00'))

    def test_csv_export_contains_only_filtered_user_rows_and_safe_text(self):
        Expense.objects.create(
            user=self.user,
            category=self.category,
            title='=SUM(1,1)',
            amount=Decimal('18.00'),
            date=timezone.localdate(),
            notes='ordinary note',
        )
        other_user = User.objects.create_user(username='other', password='A-strong-password-99')
        Category.objects.create(user=other_user, name='Private')
        Expense.objects.create(
            user=other_user,
            title='Other user record',
            amount=Decimal('30.00'),
            date=timezone.localdate(),
        )
        response = self.client.get(reverse('expense_export_csv'))
        content = response.content.decode('utf-8-sig')
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn("'=SUM(1,1)", content)
        self.assertNotIn('Other user record', content)

    def test_csv_export_rejects_invalid_filters(self):
        response = self.client.get(reverse('expense_export_csv'), {
            'min': '500',
            'max': '100',
        })
        self.assertEqual(response.status_code, 400)

    def test_dashboard_charts_and_monthly_budget_page_render(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'monthly-chart-data')
        self.assertContains(response, 'category-chart-data')
        self.assertContains(response, 'payment-chart-data')
        self.assertEqual(self.client.get(reverse('budget_list')).status_code, 200)
