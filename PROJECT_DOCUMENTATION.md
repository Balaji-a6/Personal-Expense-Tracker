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
| Database | MySQL, accessed through Django ORM |
| Configuration | `python-dotenv` (private settings stored in a `.env` file) |
| Tests | Django `TestCase` and Django test client |
| IDE | Visual Studio Code |

Bootstrap, Bootstrap Icons, and Chart.js are referenced from their public CDNs by the templates. Internet access is needed for those CDN assets.

## 4. System requirements

- Python 3.10 or newer
- MySQL server and a database account
- `mysqlclient` and `python-dotenv` packages (installed from `requirements.txt`)
- A modern web browser
- Visual Studio Code (recommended)

## 5. Installation and configuration

1. Download or clone the repository and open PowerShell in the project folder (the folder that contains `manage.py`).
2. Create and activate a virtual environment.
3. Install packages with `python -m pip install -r requirements.txt`.
4. Create an empty MySQL database named `expense_db`.
5. Create a file named `.env` in the same folder as `manage.py` and add `DB_PASSWORD=your_mysql_password`. Add `DB_NAME`, `DB_USER`, `DB_HOST`, and `DB_PORT` only if they differ from the defaults. The `.env` file is private and is not uploaded to GitHub.
6. Optionally add a private `DJANGO_SECRET_KEY` to `.env`; set `DJANGO_DEBUG=True` only for local development.
7. Run `python manage.py migrate` to create the tables. Do not delete the database or reset migrations.
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

The file `database_structure.sql` in the repository contains the table structure exported from MySQL (structure only, no user data). To recreate the database, create an empty MySQL database named `expense_db` and run `python manage.py migrate`.

## 7. Modules

| File or folder | Responsibility |
|---|---|
| `expense_tracker/settings.py` | Django configuration, `.env`-based MySQL settings, apps, templates, and static assets |
| `expense_tracker/urls.py` | Project URL routing |
| `expense_tracker/tracker/models.py` | Category, expense, and budget models and validation |
| `expense_tracker/tracker/form.py` | Registration, expense, filter, category, and budget forms |
| `expense_tracker/tracker/views.py` | Authentication, dashboard summaries, user-scoped CRUD, filters, CSV, categories, and budgets |
| `expense_tracker/tracker/urls.py` | Application routes |
| `expense_tracker/tracker/admin.py` | Django admin model registration |
| `expense_tracker/tracker/tests.py` | Automated application and security-boundary tests |
| `templates/` | Shared layout and responsive page templates |
| `static/` | Application stylesheet (`style.css`) and browser-side validation (`script.js`) |
| `database_structure.sql` | MySQL table structure export |
| `requirements.txt` | Python package dependencies |

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

Manual browser checks include desktop and narrow/mobile widths, the login and registration pages, each CRUD flow, chart rendering, CSV opening, and category-budget warnings.

## 10. Screenshots

Screenshots of the running project are stored in the `screenshots/` folder:

| Screen | File |
|---|---|
| Login page | `screenshots/login.png` |
| Dashboard | `screenshots/dashboard.png` |
| Expense list and filters | `screenshots/expenses.png` |
| Expense form | `screenshots/add-expense.png` |
| Categories | `screenshots/categories.png` |
| Monthly budgets | `screenshots/budgets.png` |

## 11. How to run

After configuration and migrations, start the project with:

```powershell
python manage.py runserver
```

Visit <http://127.0.0.1:8000/> and register a user. Use the navigation bar to manage expenses, categories, and budgets. Django admin is available at <http://127.0.0.1:8000/admin/> for an administrator account.

## 12. Conclusion

This project demonstrates practical Django full-stack development, relational model design, safe user-specific data access, form validation, CRUD workflows, reporting, responsive frontend design, and automated tests. The database is MySQL, and private settings such as the database password are kept in a `.env` file that is never uploaded to GitHub. SQLite is used only when explicitly selected for isolated checks or tests.