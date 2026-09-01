
PACKAGE_MANAGER = uv run
DOCKER_COMPOSE = docker compose

all: dev

dev:
	@$(PACKAG_MANAGER) fastaip dev

up:
	@$(PACKAG_MANAGER) up -d

ps:
	@$(DOCKER_COMPOSE) ps

db:
	@$(DOCKER_COMPOSE) exec db psql -U tsilva -d aiops

volume:
	docker volume ls

image:
	docker image ls

down:
	@$(DOCKER_COMPOSE) down

.PHONY: all dev up ps db down
