-include .env
export


PACKAGE_MANAGER = uv run
DOCKER_COMPOSE = docker compose
DOCKER_EXEC = docker exec

all: dev

dev:
	@$(PACKAGE_MANAGER) fastapi dev

up:
	@$(DOCKER_COMPOSE) up -d

ps:
	@$(DOCKER_COMPOSE) ps

db_init:
	@$(PACKAGE_MANAGER) python -m app.db.init_db

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

.PHONY: all dev up ps db_init db_audit db_show image volume down reset
