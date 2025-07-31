.PHONY: install dev build up down logs test clean

install:
	poetry install

dev:
	source .venv/bin/activate && python -m uvicorn core.main:app --reload --port 8000

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

status:
	docker-compose ps

clean:
	docker-compose down -v
	docker system prune -f
