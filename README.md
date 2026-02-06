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

## Mobility Assessment + Auto Prescription
- Create assessments at `/members/{id}` in **Mobility** section.
- Rule engine applies WiseFitt protocol:
  - Unilateral final score uses `min(left, right)`.
  - Pain flag forces score 1.
  - Priority and plan generation triggers by low scores.
- Generate plan with button **Generate Mobility Plan**.
- Training module (`/bookings`) pulls 1–2 exercises from latest active mobility plan into a **Mobility Block**.

### Mobility endpoints
- `GET/POST /api/mobility/assessments/`
- `POST /api/mobility/assessments/{id}/generate_plan/`
- `GET/POST /api/mobility/exercises/` (write admin-only)
- `GET/POST /api/mobility/plans/`
- `GET /api/mobility/members/{member_id}/latest/`
- `GET /api/mobility/members/{member_id}/block/`

### Seed mobility exercises
- `python manage.py seed_data` now seeds mobility exercise library (ankle/hip/thoracic/shoulder/stability).

## Important API endpoints
- `POST /api/leads/{id}/convert/`
- `POST /api/leads/{id}/mark_lost/`
- `GET /api/metrics/conversion/?days=30&source=Meta`
- `GET /api/members-overview/`
- `GET /openapi/`
