# WiseFitt Premium Gym Platform (MVP)

## Assumptions
- Single-location deployment for MVP; service lines are tracked per entry.
- PostgreSQL is the production target; SQLite is used for local quickstart.
- JWT auth is implemented with access/refresh tokens.
- SGPT workout snapshots are generated from `WorkoutTemplate` at booking time.
- Functional classes use a session-level `FunctionalWOD`.

## Step 1 — Data model rationale
Core entities and links:
- **Auth/RBAC**: `User` + `Profile(role)` supports Admin, Coach, Reception, Member, Practitioner.
- **Members/Memberships**: `MemberProfile`, `MembershipPackage`, `ProductAddon`, `PackageAddon`, `Membership`.
- **Scheduling/Bookings**: `Session` with capacities (SGPT=5, Functional=12), `Booking` with waitlist/check-in states.
- **Workout Linkage**:
  - SGPT: `Booking -> WorkoutInstance(snapshot)` (member-specific snapshot).
  - Functional: `Session -> FunctionalWOD`.
- **Logging**: `WorkoutLog` linked to `Booking`.
- **Treatments**: `TreatmentType`, `TreatmentBooking` with consent checkbox and notes.
- **Finance**: `FinanceEntry` + `OverheadConfig` (allocation method).
- **CRM**: `Lead`, `LeadActivity`, `LeadTask` stages from New Lead to Churned.
- **Integrations/Attribution**: `LeadIntegrationEvent` stores raw payload + mapped fields + UTM/click IDs in `Lead`.
- **Offline conversions**: `ConversionEvent`, `OfflineConversionConnector`, `ConnectorRun` with pluggable provider interface.

## Step 1 — API endpoints
Base path: `/api/`
- Auth: `POST /auth/token/`, `POST /auth/token/refresh/`
- CRUD viewsets:
  - `/profiles/`, `/membership-packages/`, `/product-addons/`, `/package-addons/`, `/memberships/`
  - `/programs/`, `/workout-templates/`, `/sessions/`, `/bookings/`, `/workout-instances/`, `/workout-logs/`
  - `/functional-wods/`, `/treatment-types/`, `/treatment-bookings/`
  - `/finance-entries/` (+ `GET /finance-entries/dashboard/`)
  - `/leads/`, `/lead-activities/`, `/lead-tasks/`, `/conversion-events/`
  - `/overhead-configs/`, `/offline-connectors/` (+ `POST /offline-connectors/{id}/run/`), `/connector-runs/`
- TV screens:
  - `GET /screens/sgpt/`
  - `GET /screens/functional/`
- Integrations/automations:
  - `POST /integrations/leads/webhook/` (generic ingest + dedupe)
  - `POST /crm/leads/{lead_id}/consultation-booked/`
- OpenAPI: `GET /openapi/`

## Step 1 — Frontend routes/pages
`frontend/app`:
- `/` dashboard
- `/tv/sgpt` SGPT room screen
- `/tv/functional` Functional room screen
- `/members`, `/bookings`, `/treatments`, `/finance`, `/crm`, `/login`

## Step 2 — Backend implementation summary
- Django + DRF with JWT authentication and RBAC-ready profile roles.
- Booking flow auto-creates SGPT `WorkoutInstance` snapshot and enforces waitlist on capacity.
- Functional screen reads session `FunctionalWOD` for active class.
- CRM lead webhook ingestion stores raw payload, attribution fields, dedupes by email/phone.
- Finance dashboard returns income/expense/margin/service-line/ARPU/churn.
- Offline conversion connectors implemented as provider interfaces with stub adapters.

## Step 3 — Frontend implementation summary
- Next.js + TypeScript + Tailwind-ready structure.
- Mobile-first dark UI shell and module pages.
- TV pages fetch and render live SGPT/Functional screen payloads.

## Step 4 — Seed, tests, and setup
### Seed command
- Creates: 2 coaches, 2 practitioners, 20 members, 50 leads, 1-week SGPT/Functional sessions, sample SGPT template + WODs, sample finance entries, memberships, treatment booking.

```bash
python manage.py seed_data
```

### Local setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install django djangorestframework djangorestframework-simplejwt
python manage.py makemigrations gymapp
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Deployment notes
- Configure PostgreSQL and set `DATABASES` accordingly.
- Set secure `SECRET_KEY`, `DEBUG=False`, trusted `ALLOWED_HOSTS`.
- Add CORS/cookie strategy if frontend served separately.
- For offline conversions, replace stub providers in `gymapp/integrations.py`.
