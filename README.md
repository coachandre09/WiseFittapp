# WiseFitt Premium Gym Platform

## Backend (Django)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver 0.0.0.0:8000
```

### Optional PostgreSQL
```bash
docker compose up -d db
export DB_ENGINE=postgres
export POSTGRES_DB=wisefitt
export POSTGRES_USER=wisefitt
export POSTGRES_PASSWORD=wisefitt
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
python manage.py migrate
```

## Frontend (Next.js)
```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api npm run dev -- --host 0.0.0.0 --port 3000
```

## CRM flow implemented
- Login with JWT (`/api/auth/token/` + refresh).
- Dashboard conversion metrics with filters by `days` and `source` via `/api/metrics/conversion/`.
- Prospects list with search/filter/add/convert/mark lost.
- Prospect detail with editable fields, activities, tasks, conversion CTA.
- Members list via `/api/members-overview/`.

## Important API endpoints
- `POST /api/leads/{id}/convert/`
- `POST /api/leads/{id}/mark_lost/`
- `GET /api/metrics/conversion/?days=30&source=Meta`
- `GET /api/members-overview/`
- `GET /openapi/`
