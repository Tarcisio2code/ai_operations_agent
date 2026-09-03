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
	@$(DOCKER_EXEC) $(CONTAINER_NAME) psql -U $(DATABASE_USER) -d $(DATABASE_NAME) -c "\d+ tickets"

db_show:
	@$(DOCKER_EXEC) $(CONTAINER_NAME) psql -U $(DATABASE_USER) -d $(DATABASE_NAME) -x -c "SELECT * from tickets;"

volume:
	docker volume ls

image:
	docker image ls

down:
	@$(DOCKER_COMPOSE) down

reset:
	@$(DOCKER_COMPOSE) down -v

.PHONY: all dev up ps db_init db_audit db_show image volume down reset
