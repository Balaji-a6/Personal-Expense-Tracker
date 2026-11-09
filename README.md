# Personal Expense Tracker (Paisa)

**Student:** Balaji A  
**Project type:** Individual Python Full Stack Project

Paisa is a Django application for recording personal expenses, organizing them into private categories, and understanding spending with monthly summaries, charts, and budgets.

## Project objectives

- Practice Django models, forms, views, templates, URL routing, and authentication.
- Provide private expense records and categories for each account.
- Make it easy to add, search, filter, update, and remove expenses.
- Summarize monthly, yearly, category, and payment-method spending.
- Provide monthly category budgets and CSV downloads.

## Technologies

- Python 3.10 or newer
- Django 5.2
- MySQL with `mysqlclient` (the database engine already configured by this project)
- HTML, CSS, Bootstrap 5, Bootstrap Icons, and JavaScript
- Chart.js for the dashboard charts

## Requirements

- Python and pip
- MySQL server reachable from this computer
- A MySQL database and user with permission to create or update the project tables
- A modern browser

## Installation

Open PowerShell at the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Set-Location .\expense_tracker
```

Set the connection settings in the current PowerShell session. The database name, host, port, and username default to the values used by the existing project; set the password privately rather than saving it in source code:

```powershell
$env:DB_ENGINE = "mysql"
$env:DB_NAME = "expense_db"
$env:DB_USER = "root"
$env:DB_PASSWORD = "your-local-mysql-password"
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"
$env:DJANGO_SECRET_KEY = "generate-a-private-django-secret"
$env:DJANGO_DEBUG = "True"
```

Use your own MySQL username/password if they differ. Do not commit credentials, secret keys, database dumps, or environment files. If `DJANGO_SECRET_KEY` is not set, a temporary random key is generated at startup and sessions will not survive a server restart. Set a private key for normal use and deployment. If the database password previously stored in settings was real, rotate it in MySQL and update your local environment.

## Database setup

The project uses the existing MySQL backend and the migrations in `expense_tracker/tracker/migrations/`. Run pending migrations without deleting or resetting the database:

```powershell
python manage.py migrate
```

The application has three main data models:

- **User:** Django's built-in account model; Django stores passwords as secure hashes.
- **Category:** belongs to one user; category names are unique per user.
- **Expense:** belongs to one user and may reference a category; amount, date, method, and notes are stored with the transaction.
- **Budget:** belongs to one user and category; one monthly spending limit per category.

Expenses and categories are always queried for the signed-in user. A category supplied by another user is rejected.

## Run the project

Create an administrator if desired, then start the development server:

```powershell
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Register an account or log in. Django's default password validators are applied during registration.

## Main features

- Registration, login, POST-based logout, and authenticated pages.
- User-scoped expense and category data.
- Expense CRUD with title, amount, category, date, payment method, and notes.
- Server-side checks for positive amounts, required fields, and non-future dates, with matching browser validation.
- Expense search by title or notes; category, date-range, and amount filters; pagination; and clear-filters link.
- CSV download using the active filters.
- Dashboard totals, recent expenses, monthly category and payment charts, and a year-by-month chart.
- Per-category monthly budgets with remaining/over-budget amounts.
- Responsive Bootstrap layout, messages, and a POST confirmation before deleting an expense.

## Tests

The project tests registration, login/logout, validation, expense CRUD, filters, pagination, CSV export, category handling, budget progress, and user-data isolation. They can run against an isolated in-memory SQLite database without connecting to MySQL:

```powershell
$env:DB_ENGINE = "sqlite"
$env:DB_NAME = ":memory:"
python manage.py check
python manage.py test
```

This override is only for local checks and tests; the normal configured database remains MySQL.

## Screenshots

Add your own screenshots in a `screenshots/` folder at the repository root before submission:

- Dashboard: `screenshots/dashboard.png`
- Expense list and filters: `screenshots/expenses.png`
- Add expense form: `screenshots/add-expense.png`

## GitHub preparation

The included `.gitignore` excludes local databases, secrets/environment files, Python caches, and development environments. Before uploading, confirm that no credentials, database records, or personal environment files are staged.

## Conclusion

Paisa demonstrates a complete Django workflow: authentication, relational data, protected CRUD operations, validation, filtering, reporting, responsive templates, and automated tests.
