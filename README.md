<div align="center">

# Exam Tickets Generator

**A Django web application for generating and managing randomized university examination tickets**

[![Django](https://img.shields.io/badge/Django-6.0.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-dev-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-prod-499848?style=for-the-badge&logo=gunicorn&logoColor=white)](https://gunicorn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-F7DF1E?style=for-the-badge)](LICENSE)

[Getting Started](#getting-started) · [Features](#features) · [Deployment](#deployment) · [Contributing](#contributing)

</div>

---

## About

**Exam Tickets Generator** is a web application built for universities and educational institutions. It allows instructors to maintain a question bank across multiple subjects and instantly generate numbered, randomized examination tickets — one click to produce a balanced set of questions drawn from the pool.

The interface is entirely in Russian (locale `ru-ru`) and covers five mathematics and physics disciplines typically found in university curricula.

---

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Data Models](#data-models)
- [URL Reference](#url-reference)
- [Deployment](#deployment)
  - [Prepare the environment](#1-prepare-the-environment)
  - [Gunicorn](#2-gunicorn)
  - [Nginx reverse proxy](#3-nginx-reverse-proxy)
  - [Railway / Heroku](#4-railway--heroku)
- [Security](#security)
- [Commands Reference](#commands-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature | Description |
|---|---|
| **Ticket Generation** | One-click generation of a randomized exam ticket with 5 questions drawn from the question bank |
| **Sequential Numbering** | Each ticket gets an auto-incremented number per subject, tracked by `TicketCounter` |
| **Multi-Subject Support** | Five university disciplines — Algorithm Analysis, Complex Analysis, Differential Equations, Numerical Methods, Physics |
| **Question Types** | Questions are tagged as *Theory* or *Practice* for balanced ticket composition |
| **Difficulty Levels** | Physics questions carry a difficulty rating (1–5) for fine-grained selection |
| **Question Management** | Add questions individually or in bulk, filter by subject/type, export and import |
| **Admin Panel** | Full Django admin interface with search, filters, and inline editing |
| **Sample Data** | `load_sample_data` management command seeds the database for quick demos |
| **Responsive UI** | Clean interface using the Manrope font family, works on desktop and mobile |
| **Production-ready config** | Security headers, HSTS, CSRF/session cookie protection — all auto-enabled when `DEBUG=False` |

---

## Demo

> Add screenshots here after running the application locally.

```
screenshots/
├── home.png          ← Ticket list page
├── ticket.png        ← Generated ticket detail
├── questions.png     ← Question management with filters
└── admin.png         ← Django admin panel
```

To capture screenshots, run the app locally (`python manage.py runserver`),
load sample data (`python manage.py load_sample_data`), and visit `http://localhost:8000`.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Framework | [Django 6.0.1](https://djangoproject.com) | Web framework, ORM, admin |
| Language | Python 3.10+ | Backend logic |
| Database | SQLite / PostgreSQL | Development / Production |
| WSGI Server | [Gunicorn 25.0](https://gunicorn.org) | Production HTTP server |
| Config | [python-decouple 3.8](https://github.com/henriquebastos/python-decouple) | `.env` → settings |
| Frontend | HTML5 + CSS3, [Manrope](https://fonts.google.com/specimen/Manrope) | Templates, styling |

---

## Getting Started

### Prerequisites

- Python **3.10** or higher
- `pip`
- Git

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/exam-tickets-django.git
cd exam-tickets-django/exam_tickets_django
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Apply database migrations**

```bash
python manage.py migrate
```

**5. (Optional) Seed sample data**

```bash
python manage.py load_sample_data
```

**6. Create a superuser for the admin panel**

```bash
python manage.py createsuperuser
```

**7. Start the development server**

```bash
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

### Configuration

Copy the example environment file and fill in values:

```bash
cp .env.example .env
```

Generate a secure `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**All available variables:**

| Variable | Description | Default | Required |
|---|---|---|---|
| `SECRET_KEY` | Django cryptographic secret | — | **Yes** |
| `DEBUG` | Enable debug mode and error pages | `False` | No |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | `localhost,127.0.0.1` | No |
| `DATABASE_URL` | PostgreSQL connection string | SQLite file | No |
| `SECURE_SSL_REDIRECT` | Redirect all HTTP requests to HTTPS | `True` (prod) | No |
| `SECURE_HSTS_SECONDS` | HSTS `max-age` header value in seconds | `31536000` | No |

> **Note:** When `DEBUG=False`, the following security settings are enabled **automatically** — no additional configuration needed:
> `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`,
> `SECURE_HSTS_PRELOAD`, `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS = 'DENY'`.

---

## How It Works

```
User clicks "Generate Ticket"
        │
        ▼
generate_ticket() view
        │
        ├─ Queries all Question objects for the selected subject
        ├─ Randomly picks 5 questions with random.sample()
        ├─ Creates a new Ticket object
        ├─ Links the 5 questions via M2M relationship (ticket.questions.set(...))
        └─ Renders ticket.html with the result

TicketCounter
        │
        └─ Per-subject counter incremented on each generation
           so tickets are numbered: Билет №1, Билет №2, ...
```

---

## Data Models

### `Question`

The core entity — a single exam question.

| Field | Type | Description |
|---|---|---|
| `subject` | `CharField` (choices) | One of 5 subjects (see below) |
| `type` | `CharField` (choices) | `theory` or `practice` |
| `text` | `TextField` | Full question text |
| `difficulty` | `IntegerField` (nullable) | 1–5, used for Physics only |
| `created_at` | `DateTimeField` | Auto-set on creation |
| `updated_at` | `DateTimeField` | Auto-updated on save |

**Subjects:**

| Key | Display name |
|---|---|
| `analysis` | Анализ Алгоритмов |
| `complex` | Комплексный Анализ |
| `differential` | Дифференциальные уравнения |
| `numerical` | Численные методы |
| `physics` | Физика |

### `TicketCounter`

Tracks the sequential ticket number per subject so numbering never resets.

| Field | Type | Description |
|---|---|---|
| `subject` | `CharField` (unique) | Subject key |
| `last_number` | `IntegerField` | Last issued ticket number |

### `Ticket`

A generated exam ticket. Holds a many-to-many relationship to `Question`.

| Field | Type | Description |
|---|---|---|
| `questions` | `ManyToManyField → Question` | The 5 selected questions |
| `created_at` | `DateTimeField` | Generation timestamp |

---

## URL Reference

| Method | URL | View | Description |
|---|---|---|---|
| `GET` | `/` | `index` | List all generated tickets |
| `GET` | `/generate/` | `generate_ticket` | Generate a new random ticket |
| `GET` | `/questions/` | `questions_list` | Browse questions; filter with `?subject=<key>` |
| `GET/POST` | `/questions/add-bulk/` | `add_bulk_questions` | Bulk-add questions from a form |
| `POST` | `/questions/<id>/delete/` | `delete_question` | Delete a single question |
| `GET` | `/questions/export/` | `export_questions` | Export all questions |
| `POST` | `/questions/import/` | `import_questions` | Import questions from a file |
| `GET/POST` | `/admin/` | Django admin | Admin panel |

---

## Deployment

### 1. Prepare the environment

```ini
# .env (production)
DEBUG=False
SECRET_KEY=<generate-with-get_random_secret_key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

Collect static files:

```bash
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py check --deploy   # must pass with no issues
```

### 2. Gunicorn

```bash
gunicorn exam_tickets.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120
```

### 3. Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /static/ {
        alias /path/to/project/staticfiles/;
    }

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

### 4. Railway / Heroku

A `Procfile` is already included:

```
web: gunicorn exam_tickets.wsgi --bind 0.0.0.0:$PORT
```

Set the environment variables via the platform dashboard (or `railway variables set` / `heroku config:set`) and deploy.

---

## Security

### Production checklist

- [ ] `.env` is in `.gitignore` and never committed
- [ ] `SECRET_KEY` is unique per environment and never reused
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` contains only your domain(s)
- [ ] HTTPS is terminated at the server / load balancer
- [ ] `SECURE_SSL_REDIRECT=True` set in `.env`
- [ ] `python manage.py check --deploy` passes with no warnings
- [ ] Database user has least-privilege permissions

### Security headers (auto-applied when `DEBUG=False`)

| Header | Setting | Value |
|---|---|---|
| HSTS | `SECURE_HSTS_SECONDS` | 31 536 000 s (1 year) |
| HSTS subdomains | `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` |
| HSTS preload | `SECURE_HSTS_PRELOAD` | `True` |
| X-Frame-Options | `X_FRAME_OPTIONS` | `DENY` |
| Content-Type sniffing | `SECURE_CONTENT_TYPE_NOSNIFF` | `True` |
| Secure cookies | `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` | `True` |

---

## Commands Reference

```bash
# Database
python manage.py migrate                   # Apply all pending migrations
python manage.py makemigrations            # Create new migrations after model changes

# Data
python manage.py load_sample_data          # Seed database with example questions
python manage.py createsuperuser           # Create an admin user

# Static files
python manage.py collectstatic --no-input  # Collect static files for production

# Checks
python manage.py check                     # System check
python manage.py check --deploy            # Production readiness check

# Shell
python manage.py shell                     # Open interactive Django shell

# Tests
python manage.py test                      # Run all tests
python manage.py test tickets              # Run tests for the tickets app
```

---

## Troubleshooting

<details>
<summary><b>ModuleNotFoundError on startup</b></summary>

The virtual environment is not activated or dependencies are not installed.

```bash
# Activate the environment
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

</details>

<details>
<summary><b>SECRET_KEY not set / ImproperlyConfigured</b></summary>

`python-decouple` could not find `SECRET_KEY` in the `.env` file.

```bash
cp .env.example .env
# Open .env and set SECRET_KEY to a generated value:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

</details>

<details>
<summary><b>"Not enough questions to generate a ticket"</b></summary>

The question bank has fewer than 5 questions. Load sample data:

```bash
python manage.py load_sample_data
```

Or add questions manually via the admin panel at `/admin/` or the bulk-add page at `/questions/add-bulk/`.

</details>

<details>
<summary><b>Static files not loading in production</b></summary>

```bash
python manage.py collectstatic --no-input
```

Make sure `STATIC_ROOT` is served by Nginx or your hosting platform.

</details>

---

## Project Structure

```
exam_tickets_django/
├── exam_tickets/                    # Django project package
│   ├── settings.py                  # All settings — driven by .env via python-decouple
│   ├── urls.py                      # Root URL configuration
│   ├── wsgi.py                      # WSGI entry point (Gunicorn)
│   └── asgi.py                      # ASGI entry point (Daphne/Uvicorn)
│
├── tickets/                         # Main application
│   ├── models.py                    # Question, TicketCounter models
│   ├── views.py                     # View functions
│   ├── urls.py                      # App-level URL routing
│   ├── admin.py                     # Admin panel configuration
│   ├── apps.py                      # App config
│   ├── tests.py                     # Test cases
│   └── management/
│       └── commands/
│           └── load_sample_data.py  # DB seeding command
│
├── templates/
│   └── tickets/
│       ├── base.html                # Base layout, fonts, global styles
│       ├── index.html               # Home — ticket list
│       ├── ticket.html              # Ticket detail view
│       └── questions.html           # Question management + filters
│
├── .env.example                     # Environment variable template
├── .env                             # Local secrets (not committed)
├── .gitignore
├── Procfile                         # Process definition for Railway / Heroku
├── requirements.txt
└── manage.py
```

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests if applicable
4. Run the test suite: `python manage.py test`
5. Commit: `git commit -m "feat: describe your change"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request — describe what you changed and why

Please keep pull requests focused on a single change. For large features, open an issue first to discuss the approach.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with [Django](https://djangoproject.com) · Python 3.10+

</div>
