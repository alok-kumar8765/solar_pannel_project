# S.K Bright Solar Energy — Django starter

A responsive Django website starter with a public solar catalogue, appointment enquiries, staff dashboard, branches, employee roles, assignment and enquiry status updates.

## Requirements
- Windows 10/11
- Python 3.11 or newer
- Internet connection for initial package installation (Google Fonts and Unsplash hero imagery are remote assets)

## Run locally (Windows PowerShell)
```powershell
cd sk_bright_solar_django
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations core
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/ for the website and http://127.0.0.1:8000/admin/ for administration.

## First-time setup
1. Sign in to `/admin/` with the superuser.
2. Create one or more **Branches**.
3. Create **Users** in Django Admin, then create matching **Employee Profiles** and select a role and branch. Alternatively, sign in as superuser and use **Dashboard → Add Employee**.
4. Add **Solar Products**. Add real product photos, descriptions, capacities, and prices only after confirming them.
5. Set product `is_active` on and optionally mark featured products.
6. Customer appointment requests appear on the staff dashboard and in Django Admin.

## Roles in this starter
- **Owner / S.K.**: superuser or an EmployeeProfile with role `owner`; can see all enquiries and create employee accounts.
- **Branch Manager**: sees enquiries for the assigned branch and can assign field staff from the same branch.
- **Field Employee**: sees assigned enquiries and can update their status.
- **Sales / Accounts**: currently have read-only access to enquiries assigned to their user; customize permissions before real use.
- **Customer**: public pages, product details, appointment and contact forms; no account required.

## Important limitations before public deployment
This is a runnable starter, not a production-ready ERP:
- Login/logout audit trail, attendance/presence reporting, per-action audit logs, CSV exports, dashboard charts and granular permissions are not yet implemented.
- Branch assignment is not automatic from customer city. Add an area/pincode-to-branch mapping rule before relying on routing.
- The contact form saves enquiries but does not send email. Add verified SMTP credentials and privacy/consent copy if email notifications are required.
- WhatsApp links open a chat; they do not send automated messages. The customer phone is stored as entered, so normalize country codes before generating staff WhatsApp links.
- Review cards are intentionally not fabricated. The website asks for verified reviews instead.
- Gallery uses a placeholder. Upload genuine project images before publishing.
- The Google Maps area is a placeholder. Add a verified embed URL for the business location.
- The website references Unsplash and Google Fonts remotely. For fully self-hosted, privacy-conscious and low-bandwidth delivery, download licensed images and fonts and serve them from static/media.
- Django Admin is used for branch, catalogue and detailed record management. The basic dashboard UI is deliberately small.
- The default database is SQLite for local development. For production use PostgreSQL, HTTPS, environment-based secrets, backups, monitoring, rate limiting, secure file upload validation, and a tested deployment process.
- Before launch, configure `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, secure cookies, CSRF trusted origins, static/media storage, backups, email, and a real database.
- Do not expose `/admin/` or staff accounts without strong passwords, access reviews and HTTPS.
- A branch manager's dashboard currently shows up to 100 recent enquiries; add pagination before larger datasets.

## Architecture
- `config/`: Django settings and URL routing
- `core/models.py`: Branch, EmployeeProfile, SolarProduct, Appointment, ContactMessage
- `core/forms.py`: server-side form validation
- `core/views.py`: public pages, staff dashboard, assignment and status actions
- `templates/`: reusable base and page templates
- `static/`: responsive CSS and lightweight JavaScript

## Brand contact details configured
- Call: 7398406469
- WhatsApp: 7307402720
- Location: Ramnagar, Varanasi, Uttar Pradesh
- Service area: Uttar Pradesh

Prices and product descriptions are database-managed; no unsupported business statistics or fake customer reviews are included.
