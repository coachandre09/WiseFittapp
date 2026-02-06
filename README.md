# WiseFitt Premium Gym Platform (MVP)

## Assumptions
- Single-location deployment for MVP; service lines are tracked per entry.
- SQLite default for local dev; PostgreSQL optional via env vars.
- JWT auth is implemented with access/refresh tokens.
- SGPT workout snapshots are generated from `WorkoutTemplate` at booking time.
- Functional classes use a session-level `FunctionalWOD`.

## Data model rationale (high level)
- **RBAC**: `User + Profile(role)` for Admin, Coach, Reception, Member, Practitioner.
- **Members/Memberships**: `MemberProfile`, `MembershipPackage`, `ProductAddon`, `PackageAddon`, `Membership`.
- **Scheduling/Bookings**: `Session` (capacity/room/type), `Booking` (booked/waitlist/check-in).
- **Booking -> Workout -> Screen linkage**:
  - SGPT: `Booking -> WorkoutInstance(snapshot)`.
  - Functional: `Session -> FunctionalWOD`.
- **Logging**: `WorkoutLog` linked to booking.
- **Treatments**: `TreatmentType`, `TreatmentBooking` with consent + notes.
- **Finance**: `FinanceEntry`, `OverheadConfig`.
- **CRM**: `Lead`, `LeadActivity`, `LeadTask`, `ConversionEvent`.
- **Integrations**: `LeadIntegrationEvent`, `OfflineConversionConnector`, `ConnectorRun`.

## API endpoints (base: `/api/`)
- Auth: `POST /auth/token/`, `POST /auth/token/refresh/`
- Core CRUD: profiles, memberships/packages/addons, programs/templates, sessions/bookings/workouts/logs,
  treatments, finance, CRM, connectors.
- Screens:
  - `GET /screens/sgpt/`
  - `GET /screens/functional/`
- Integrations:
  - `POST /integrations/leads/webhook/`
  - `POST /crm/leads/{lead_id}/consultation-booked/`
- OpenAPI: `GET /openapi/`

## Frontend routes
- `/` dashboard
- `/tv/sgpt`
- `/tv/functional`
- `/members`, `/bookings`, `/treatments`, `/finance`, `/crm`, `/login`

---

## ✅ Pronto para teste (rápido)

### Opção 1: Local (SQLite)
```bash
make setup
make seed
make test
make run
```

### Opção 2: Backend manual
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py test -v 2
python manage.py runserver
```

### Opção 3: PostgreSQL (com Docker)
```bash
docker compose up -d db
export DB_ENGINE=postgres
export POSTGRES_DB=wisefitt
export POSTGRES_USER=wisefitt
export POSTGRES_PASSWORD=wisefitt
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment notes
- Set secure `SECRET_KEY`, `DEBUG=False`, and proper `ALLOWED_HOSTS`.
- Add CORS policy if frontend is hosted separately.
- Replace stub adapters in `gymapp/integrations.py` for real ad platform exports.
