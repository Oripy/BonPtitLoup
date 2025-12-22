# Daycare Center Web Application

A Django web application for managing a daycare center where parents can register their children and vote on date groups (Doodle-like functionality) created by administrators.

## Features

### For Parents
- User registration and authentication
- Register and manage multiple children (name and birth date)
- View parent dashboard with all registered children
- Vote on date groups created by administrators (Yes/No/Maybe for each date option)
- View voting results

### For Administrators
- Create and manage date groups with multiple date options
- View detailed voting results with statistics
- Export voting results to CSV or Excel
- Toggle active/inactive status for date groups

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create a superuser (optional, for Django admin):
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

## Usage

### Creating Users

1. Navigate to `/accounts/register/` to create a new account
2. Choose your role: Parent or Administrator
3. Fill in your details and submit

### For Parents

1. After logging in, you'll be redirected to the children dashboard
2. Click "Add Child" to register a child with name and birth date
3. Navigate to "Vote" in the menu to see available date groups
4. Click "Vote" on a date group to vote Yes/No/Maybe for each date option
5. View results by clicking "View Results" on any date group

### For Administrators

1. After logging in, you'll be redirected to the admin panel
2. Click "Create Date Group" to create a new voting group
3. Add multiple date options (with optional start/end times)
4. View results and statistics for each date group
5. Export results to CSV or Excel format

## Project Structure

```
daycare_app/
├── accounts/          # User authentication and registration
├── children/          # Child management for parents
├── voting/            # Date group voting system
├── admin_panel/       # Administrative panel for date groups
└── daycare_project/   # Main project configuration
```

## Technologies Used

- Django 5.2.9
- Tailwind CSS (via CDN)
- django-crispy-forms
- openpyxl (for Excel export)

## Security

- CSRF protection enabled
- User authentication required for all views
- Permission checks: parents can only manage their own children
- Admin-only access to admin panel views
- SQL injection protection via Django ORM

