# Project Documentation: Personal Expense Tracker

**Student Name:** Balaji A  
**Project Title:** Personal Expense Tracker  
**Project Type:** Individual Python Full Stack Project

## 1. Introduction

The Personal Expense Tracker (Paisa) is a web application for keeping track of personal spending. A user can securely register, record transactions, group them into categories, view spending summaries, and set monthly category limits.

## 2. Objectives

1. Build a full-stack application using Python and Django.
2. Store financial information in a relational database.
3. Keep each account's expenses and categories private.
4. Implement secure account registration, login, and logout.
5. Demonstrate validated create, read, update, and delete operations.
6. Present useful summaries and reports through a responsive interface.

## 3. Technologies used

| Area | Technology |
|---|---|
| Backend | Python, Django 5.2 |
| Frontend | HTML, CSS, Bootstrap 5, JavaScript |
| Charts | Chart.js |
| Icons | Bootstrap Icons |
| Database | Existing MySQL configuration, accessed through Django ORM |
| Tests | Django `TestCase` and Django test client |
| IDE | Visual Studio Code |

Bootstrap, Bootstrap Icons, and Chart.js are referenced from their public CDNs by the templates. Internet access is needed for those CDN assets.

## 4. System requirements

- Python 3.10 or newer
- MySQL server and a database account
- `mysqlclient` package (installed from `requirements.txt`)
- A modern web browser
- Visual Studio Code (recommended)

## 5. Installation and configuration

1. Open PowerShell at the repository root.
2. Create and activate a virtual environment.
3. Install packages with `python -m pip install -r requirements.txt`.
4. Change into the Django project folder with `Set-Location .\expense_tracker`.
5. Set `DB_ENGINE=mysql` and the `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` environment variables for the existing MySQL server.
6. Set a private `DJANGO_SECRET_KEY`; set `DJANGO_DEBUG=True` only for local development.
7. Run `python manage.py migrate` to apply pending migrations. Do not delete the database or reset migrations.
8. Optionally create an administrator with `python manage.py createsuperuser`.
9. Start the server with `python manage.py runserver`, then browse to <http://127.0.0.1:8000/>.

For isolated tests, set `DB_ENGINE=sqlite` and `DB_NAME=:memory:` in the terminal before running `python manage.py check` or `python manage.py test`. The default project database remains MySQL.

## 6. Database design

The Django ORM maps the application models to relational tables:

- `auth_user` (Django): account name, email, password hash, and account metadata.
- `tracker_category`: category name and a foreign key to its owner. Category names are unique per user.
- `tracker_expense`: owner and optional category foreign keys, title, decimal amount, date, payment method, notes, and creation timestamp.
- `tracker_budget`: owner and category foreign keys with a monthly decimal spending limit. A user can have one budget per category.

Deleting a user deletes that user's categories, expenses, and budgets. Deleting a category leaves existing expenses in place as uncategorized records. Django handles password hashing and database parameterization.

## 7. Modules

| File or folder | Responsibility |
|---|---|
| `expense_tracker/expense_tracker/settings.py` | Django configuration, environment-based MySQL settings, apps, templates, and static assets |
| `expense_tracker/expense_tracker/urls.py` | Project URL routing |
| `expense_tracker/expense_tracker/tracker/models.py` | Category, expense, and budget models and validation |
| `expense_tracker/expense_tracker/tracker/form.py` | Registration, expense, filter, category, and budget forms |
| `expense_tracker/expense_tracker/tracker/views.py` | Authentication, dashboard summaries, user-scoped CRUD, filters, CSV, categories, and budgets |
| `expense_tracker/expense_tracker/tracker/urls.py` | Application routes |
| `expense_tracker/expense_tracker/tracker/admin.py` | Django admin model registration |
| `expense_tracker/expense_tracker/tracker/tests.py` | Automated application and security-boundary tests |
| `expense_tracker/templates/` | Shared layout and responsive page templates |
| `static/` | Application stylesheet and browser-side validation |

## 8. Main features

- Account registration with password validators and duplicate email/username handling.
- Login, logout, and authentication protection for personal pages.
- Expense creation, listing, editing, and deletion.
- Search by title or note; category, date, and amount filtering; pagination; and filter reset.
- CSV report download that follows current filters.
- Dashboard cards for monthly, annual, all-time totals, and transaction count.
- Category and payment-method breakdowns, recent transactions, and a current-year monthly chart.
- Monthly per-category budgets, progress indicators, remaining amounts, and over-budget warnings.
- Server-side Django validation and client-side validation for required expense fields, positive amount, future dates, and matching passwords.
- Responsive Bootstrap styling and success/error messages.

## 9. Testing and verification

Run the system check and automated tests with a temporary in-memory SQLite database:

```powershell
$env:DB_ENGINE = "sqlite"
$env:DB_NAME = ":memory:"
python manage.py check
python manage.py test
```

The tests cover registration and password hashing, authentication, user-specific record access, expense create/edit/delete, validation, search and filters, pagination, category uniqueness, budget calculations, charts, and CSV export.

Manual browser checks should include desktop and narrow/mobile widths, the login and registration pages, each CRUD flow, chart rendering, CSV opening, and category-budget warnings. Screenshots should be captured from the running local project and added to `screenshots/`.

## 10. Screenshots

Add project screenshots in a `screenshots/` folder at the repository root before final submission:

| Screen | File |
|---|---|
| Dashboard | `screenshots/dashboard.png` |
| Expense list and filters | `screenshots/expenses.png` |
| Expense form | `screenshots/add-expense.png` |
| Monthly budgets | `screenshots/budgets.png` |

## 11. How to run

After configuration and migrations, start the project with:

```powershell
python manage.py runserver
```

Visit <http://127.0.0.1:8000/> and register a user. Use the navigation bar to manage expenses, categories, and budgets. Django admin is available at <http://127.0.0.1:8000/admin/> for an administrator account.

## 12. Conclusion

This project demonstrates practical Django full-stack development, relational model design, safe user-specific data access, form validation, CRUD workflows, reporting, responsive frontend design, and automated tests. The configured database remains MySQL; SQLite is used only when explicitly selected for isolated checks or tests.
