# PracticalDesk Account app

This app uses Django's built-in `django.contrib.auth.models.User` and Simple JWT.
It does not define a custom user model.

## 1. Install dependencies

```bash
pip install djangorestframework djangorestframework-simplejwt
```

For refresh-token blacklisting, use the blacklist app included with Simple JWT.

## 2. Django settings.py

Add these apps to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # Django apps...
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "Account",
]
```

Add/merge these settings:

```python
from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

Do not replace existing settings blindly; merge these values with your project configuration.

Set the frontend reset page URL:

```python
ACCOUNT_PASSWORD_RESET_URL = "http://localhost:5173/reset-password"
```

Configure email. For local development, you can temporarily use:

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "PracticalDesk <noreply@practicaldesk.local>"
```

The reset link will print in the Django terminal. For production, configure a real SMTP provider and HTTPS frontend URL.

## 3. Project urls.py

Include the account routes:

```python
from django.urls import include, path

urlpatterns = [
    # Your other routes...
    path("api/account/", include("Account.urls")),
]
```

## 4. Migrate

```bash
python manage.py migrate
```

The built-in User model is already supplied by Django. The migration command also creates Simple JWT blacklist tables.

## 5. Endpoints

Base URL: `/api/account/`

### Register
`POST /register/`

```json
{
  "email": "student@example.com",
  "first_name": "Ada",
  "last_name": "Student",
  "password": "StrongPassword123!",
  "password_confirm": "StrongPassword123!"
}
```

The server uses the email as the Django `username`, so email login works with the default User model.

### Login
`POST /login/`

```json
{
  "email": "student@example.com",
  "password": "StrongPassword123!"
}
```

Returns `access`, `refresh`, and basic user details.

### Refresh
`POST /token/refresh/`

```json
{"refresh": "YOUR_REFRESH_TOKEN"}
```

### Logout
`POST /logout/` with `Authorization: Bearer ACCESS_TOKEN`

```json
{"refresh": "YOUR_REFRESH_TOKEN"}
```

### Forgot password
`POST /password/forgot/`

```json
{"email": "student@example.com"}
```

The response does not reveal whether the email is registered. For an existing active account, the app emails a link to the configured frontend reset page with `uid` and `token` query parameters.

### Reset password
`POST /password/reset/`

```json
{
  "uid": "UID_FROM_RESET_LINK",
  "token": "TOKEN_FROM_RESET_LINK",
  "new_password": "AnotherStrongPassword123!",
  "new_password_confirm": "AnotherStrongPassword123!"
}
```

### Profile
`GET /profile/` and `PATCH /profile/` with `Authorization: Bearer ACCESS_TOKEN`.

Only `first_name` and `last_name` are editable through this endpoint. Username and email are read-only.

### Change password
`POST /password/change/` with `Authorization: Bearer ACCESS_TOKEN`

```json
{
  "current_password": "StrongPassword123!",
  "new_password": "AnotherStrongPassword123!",
  "new_password_confirm": "AnotherStrongPassword123!"
}
```

## Security notes

- Keep JWTs and secrets out of source control.
- Use HTTPS in production.
- Use a real email backend in production.
- Do not expose access or refresh tokens in URLs.
- The logout endpoint requires `rest_framework_simplejwt.token_blacklist` and its migrations.
- This implementation assumes new accounts use email as username. If your existing database has users whose username differs from their email, adjust login to look up the user by email before authenticating.
