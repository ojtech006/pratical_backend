# PracticalDesk manual OPay receipt payment patch

## Subscription
- The only available plan is ₦450 for 4 document generations.
- The ₦650 / 6-document option is removed.
- The payment request is created as `PENDING`.
- Student uploads an OPay receipt image (JPG, PNG or WEBP), maximum 2 MB. No transfer-reference field is required.
- Upload changes status to `UNDER_REVIEW`; it does not activate credits.
- An administrator checks the actual OPay transaction and approves in Django Admin.
- `APPROVED` payments can generate up to 4 documents. Existing downloads do not consume another credit.

## Add the app URLs
In the main Django project's `urls.py`, include the generator URLs under the same API prefix used by the frontend, for example:

```python
from django.urls import include, path

urlpatterns = [
    path("api/", include("generator.urls")),
]
```

If your project already has a generator URL include, update that existing include instead of adding a duplicate.

## OPay account details
Add the authorised account holder details to Django settings via environment variables (do not commit account details to source control):

```python
import os
PRACTICALDESK_OPAY_ACCOUNT_NAME = os.getenv("PRACTICALDESK_OPAY_ACCOUNT_NAME", "")
PRACTICALDESK_OPAY_ACCOUNT_NUMBER = os.getenv("PRACTICALDESK_OPAY_ACCOUNT_NUMBER", "")
```

Set those environment variables on the server. The account name should be the exact name displayed by OPay.

## API flow
1. `POST /api/payments/create/` — returns a pending payment reference and OPay transfer details.
2. `POST /api/payments/<reference>/receipt/` — multipart form upload; field name must be `receipt`.
3. `GET /api/payments/<reference>/status/` — returns `PENDING`, `UNDER_REVIEW`, `APPROVED`, or `REJECTED`.
4. Admin reviews the payment in Django Admin. Only approve after checking the incoming transfer in the OPay account.
5. `POST /api/reports/` — keep using `payment_reference`; generation is rejected until status is `APPROVED`.

## Migration
Run:

```bash
python manage.py migrate
```

## Important integration note
This ZIP contains the Django `generator` app patch only. The React frontend must remove transfer-reference input, show the single ₦450 plan, upload the selected receipt as multipart field `receipt`, and display the pending/review/approved status. The latest frontend attachment was not included in this ZIP, so its UI has not been changed here.
