-include .env
export


PACKAGE_MANAGER = uv run
DOCKER_COMPOSE = docker compose
DOCKER_EXEC = docker exec

.PHONY: all dev tests up ps db_migrate db_rev db_info db_check db_seed \
	db_audit db_show volume image down reset

all: dev

dev:
	@$(PACKAGE_MANAGER) fastapi dev

tests:
	@$(PACKAGE_MANAGER) pytest -v

up:
	@$(DOCKER_COMPOSE) up -d

ps:
	@$(DOCKER_COMPOSE) ps

db_migrate:
	@$(PACKAGE_MANAGER) alembic upgrade head

db_rev:
	@$(PACKAGE_MANAGER) alembic revision --autogenerate -m "$(m)"

db_info:
	@$(PACKAGE_MANAGER) alembic current

db_check:
	@$(PACKAGE_MANAGER) alembic check

db_seed:
	@$(PACKAGE_MANAGER) python -m app.db.seed

db_audit:
	@for table in $$(docker exec $(CONTAINER_NAME) psql -U $(DATABASE_USER) -d $(DATABASE_NAME) -t -A -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"); do \
		docker exec $(CONTAINER_NAME) psql -U $(DATABASE_USER) -d $(DATABASE_NAME) -c "\d \"$$table\";"; \
	done

db_show:
	@for table in $$(docker exec $(CONTAINER_NAME) psql -U $(DATABASE_USER) -d $(DATABASE_NAME) -t -A -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"); do \
		echo ""; \
		echo "===< $$table >==="; \
		if [ "$$table" = "tickets" ]; then \
			docker exec $(CONTAINER_NAME) psql -U $(DATABASE_USER) -d $(DATABASE_NAME) -x -c "SELECT * FROM \"$$table\";"; \
		else \
			docker exec $(CONTAINER_NAME) psql -U $(DATABASE_USER) -d $(DATABASE_NAME) -c "SELECT * FROM \"$$table\";"; \
		fi; \
	done

volume:
	docker volume ls

image:
	docker image ls

down:
	@$(DOCKER_COMPOSE) down

reset:
	@$(DOCKER_COMPOSE) down -v

.PHONY: all dev tests up ps db_init db_audit db_show image volume down reset
