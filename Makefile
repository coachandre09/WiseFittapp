.PHONY: setup test run seed frontend

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	. .venv/bin/activate && python manage.py migrate

seed:
	. .venv/bin/activate && python manage.py seed_data

test:
	./scripts/test_backend.sh

run:
	. .venv/bin/activate && python manage.py runserver

frontend:
	cd frontend && npm install && npm run dev
