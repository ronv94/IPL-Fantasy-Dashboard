DOCKER ?= docker
COMPOSE ?= $(DOCKER) compose
IMAGE ?= ipl-fantasy-dashboard
PORT ?= 8050

.PHONY: help build up stop restart logs shell clean rm-image ps

help:
	@echo "Available targets:"
	@echo "  make build      Build the Docker compose app image"
	@echo "  make up         Start the app with docker compose on localhost:$(PORT)"
	@echo "  make stop       Stop and remove the compose app"
	@echo "  make restart    Restart the compose app"
	@echo "  make logs       Tail compose logs"
	@echo "  make shell      Open a shell inside the app container"
	@echo "  make ps         Show compose service status"
	@echo "  make clean      Stop container and remove the app image"
	@echo "  make rm-image   Remove the built image"

build:
	PORT=$(PORT) $(COMPOSE) build

up:
	PORT=$(PORT) $(COMPOSE) up -d --build
	@echo "App running at http://127.0.0.1:$(PORT)"

stop:
	-PORT=$(PORT) $(COMPOSE) down

restart: stop up

logs:
	PORT=$(PORT) $(COMPOSE) logs -f app

shell:
	PORT=$(PORT) $(COMPOSE) exec app /bin/sh

ps:
	PORT=$(PORT) $(COMPOSE) ps

clean: stop
	-$(DOCKER) rmi $(IMAGE)

rm-image:
	-$(DOCKER) rmi $(IMAGE)