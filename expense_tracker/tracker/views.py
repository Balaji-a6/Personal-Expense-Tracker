import csv
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .form import BudgetForm, CategoryForm, ExpenseFilterForm, ExpenseForm, RegisterForm
from .models import Budget, Category, Expense


def _budget_progress(user, today):
    month_expenses = Expense.objects.filter(
        user=user,
        date__year=today.year,
        date__month=today.month,
    )
    spent_by_category = {
        row['category_id']: row['total']
        for row in month_expenses.values('category_id').annotate(total=Sum('amount'))
    }
    progress = []
    for budget in Budget.objects.filter(user=user).select_related('category'):
        spent = spent_by_category.get(budget.category_id, Decimal('0.00'))
        remaining = budget.monthly_limit - spent
        progress.append({
            'category': budget.category,
            'limit': budget.monthly_limit,
            'spent': spent,
            'remaining': remaining,
            'remaining_abs': abs(remaining),
            'overage': max(-remaining, Decimal('0.00')),
            'percent': min(float(spent / budget.monthly_limit * 100), 100)
            if budget.monthly_limit > 0 else 0,
            'exceeded': remaining < 0,
        })
    return progress


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account is ready.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    today = timezone.localdate()
    expenses = Expense.objects.filter(user=request.user)
    month_expenses = expenses.filter(date__year=today.year, date__month=today.month)
    year_expenses = expenses.filter(date__year=today.year)

    month_total = month_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    all_total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    year_total = year_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    category_rows = month_expenses.values('category__name').annotate(
        total=Sum('amount'),
    ).order_by('-total')
    category_chart = {
        'labels': [row['category__name'] or 'Uncategorized' for row in category_rows],
        'totals': [float(row['total']) for row in category_rows],
    }

    monthly_totals = {
        row['date__month']: float(row['total'])
        for row in year_expenses.values('date__month').annotate(total=Sum('amount'))
    }
    monthly_chart = {
        'labels': [date(today.year, month, 1).strftime('%b') for month in range(1, 13)],
        'totals': [monthly_totals.get(month, 0) for month in range(1, 13)],
    }

    payment_rows = month_expenses.values('payment_method').annotate(
        total=Sum('amount'),
    ).order_by('-total')
    payment_chart = {
        'labels': [row['payment_method'] for row in payment_rows],
        'totals': [float(row['total']) for row in payment_rows],
    }

    context = {
        'month_total': month_total,
        'all_total': all_total,
        'year_total': year_total,
        'count': expenses.count(),
        'recent': expenses.select_related('category')[:5],
        'category_chart': category_chart,
        'monthly_chart': monthly_chart,
        'payment_chart': payment_chart,
        'budgets': _budget_progress(request.user, today),
        'month_name': today.strftime('%B'),
        'year': today.year,
    }
    return render(request, 'dashboard.html', context)


def _filtered_expenses(request):
    form = ExpenseFilterForm(request.GET, user=request.user)
    expenses = Expense.objects.filter(user=request.user).select_related('category')
    if form.is_valid():
        filters = form.cleaned_data
        search = filters.get('q')
        if search:
            expenses = expenses.filter(Q(title__icontains=search) | Q(notes__icontains=search))
        if filters.get('category'):
            expenses = expenses.filter(category_id=filters['category'])
        if filters.get('start'):
            expenses = expenses.filter(date__gte=filters['start'])
        if filters.get('end'):
            expenses = expenses.filter(date__lte=filters['end'])
        if filters.get('min') is not None:
            expenses = expenses.filter(amount__gte=filters['min'])
        if filters.get('max') is not None:
            expenses = expenses.filter(amount__lte=filters['max'])
    return expenses, form


@login_required
def expense_list(request):
    expenses, form = _filtered_expenses(request)
    total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    page = Paginator(expenses, 10).get_page(request.GET.get('page'))
    return render(request, 'expense_list.html', {
        'page': page,
        'total': total,
        'filter_form': form,
    })


@login_required
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added.')
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'expense_form.html', {'form': form, 'title': 'Add expense'})


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(
        Expense.objects.select_related('category'),
        pk=pk,
        user=request.user,
    )
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated.')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    return render(request, 'expense_form.html', {'form': form, 'title': 'Edit expense'})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect('expense_list')
    return render(request, 'expense_confirm_delete.html', {'expense': expense})


@login_required
def expense_export_csv(request):
    expenses, form = _filtered_expenses(request)
    if not form.is_valid():
        return HttpResponseBadRequest('Invalid expense filters. Check your dates, amounts, and category.')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="my-expenses.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Date', 'Title', 'Category', 'Amount', 'Payment method', 'Notes'])
    for expense in expenses:
        writer.writerow([
            expense.date.isoformat(),
            _safe_csv_text(expense.title),
            _safe_csv_text(expense.category.name if expense.category else ''),
            expense.amount,
            expense.payment_method,
            _safe_csv_text(expense.notes),
        ])
    return response


def _safe_csv_text(value):
    value = str(value)
    if value.startswith(('=', '+', '-', '@', '\t', '\r')):
        return f"'{value}"
    return value


@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'category_list.html', {'categories': categories})


@login_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added.')
            return redirect('category_list')
    else:
        form = CategoryForm(user=request.user)
    return render(request, 'category_form.html', {'form': form})


@login_required
def budget_list(request):
    budgets = _budget_progress(request.user, timezone.localdate())
    return render(request, 'budget_list.html', {'budgets': budgets})


@login_required
def budget_add(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            _, created = Budget.objects.update_or_create(
                user=request.user,
                category=form.cleaned_data['category'],
                defaults={'monthly_limit': form.cleaned_data['monthly_limit']},
            )
            message = 'Monthly budget added.' if created else 'Monthly budget updated.'
            messages.success(request, message)
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)
    return render(request, 'budget_form.html', {'form': form})
